import html

import nh3
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import serializers


# Input policy for plain text fields entered by customers (task 19165).
# Keep the policy in this one function, so it can be changed later
# (e.g. strip instead of reject) without touching the callers.
def check_plain_text(value):
    if isinstance(value, str) and nh3.is_html(value):
        raise ValidationError('HTML tags are not allowed.')
    return value


# Sanitise on save (task 19165), same structure as SanitiseMixin in Apiary / DAS,
# with nh3 instead of regular expressions.

# Tags and attributes kept in fields that hold HTML (Summernote / Quill content).
# long_description holds whole pages with <style> and <link>, so they are kept too.
HTML_TAGS = set(nh3.ALLOWED_TAGS) | {"font", "style", "title", "link"}
HTML_ATTRIBUTES = {tag: set(attrs) for tag, attrs in nh3.ALLOWED_ATTRIBUTES.items()}
HTML_ATTRIBUTES["*"] = HTML_ATTRIBUTES.get("*", set()) | {"class", "style", "id", "lang", "title"}
HTML_ATTRIBUTES["a"] = HTML_ATTRIBUTES.get("a", set()) | {"target", "rel"}
HTML_ATTRIBUTES["font"] = {"color", "face", "size"}
HTML_ATTRIBUTES["link"] = {"rel", "href", "type"}
URL_SCHEMES = {"http", "https", "mailto", "tel"}


def remove_html_tags(text):
    """Plain text fields: remove every tag, keep the text between tags."""
    if text is None:
        return None
    # Without "<" there is no tag. Return the value as it is, because nh3 also
    # decodes entity names in text, e.g. "?a=1&para=2" in a URL becomes "?a=1¶=2".
    if "<" not in text:
        return text
    # nh3 returns escaped text (& -> &amp;), so unescape it. Repeat, because
    # unescaping can turn text such as "&lt;b&gt;" into a new tag.
    for _ in range(3):
        cleaned = html.unescape(nh3.clean(text, tags=set()))
        if cleaned == text:
            break
        text = cleaned
    return text


def remove_script_tags(text):
    """HTML fields: keep allowed tags and attributes, remove scripts, event attributes and unsafe links."""
    if text is None:
        return None
    return nh3.clean(
        text,
        tags=HTML_TAGS,
        attributes=HTML_ATTRIBUTES,
        clean_content_tags={"script"},
        link_rel=None,
        url_schemes=URL_SCHEMES,
    )


def remove_script_tags_nested(value):
    if isinstance(value, str):
        return remove_script_tags(value)
    if isinstance(value, list):
        return [remove_script_tags_nested(v) for v in value]
    if isinstance(value, dict):
        return {k: remove_script_tags_nested(v) for k, v in value.items()}
    return value

def sanitise_fields(instance, exclude=[], error_on_change=[]):
    if hasattr(instance, "__dict__"):
        for i in instance.__dict__:
            # remove html tags for all string fields not in the exclude list
            if i not in exclude and (isinstance(instance.__dict__[i], dict)):
                instance.__dict__[i] = sanitise_fields(instance.__dict__[i])

            elif isinstance(instance.__dict__[i], list) and i not in exclude:
                for j in range(0, len(instance.__dict__[i])):
                    check = instance.__dict__[i][j]
                    if isinstance(instance.__dict__[i][j], str):
                        instance.__dict__[i][j] = remove_html_tags(instance.__dict__[i][j])
                    elif isinstance(instance.__dict__[i][j], list) or isinstance(instance.__dict__[i][j], dict):
                        instance.__dict__[i][j] = sanitise_fields(instance.__dict__[i][j])
                    if i in error_on_change and check != instance.__dict__[i][j]:
                        raise serializers.ValidationError("html tags included in field")

            elif isinstance(instance.__dict__[i], str) and i not in exclude:
                check = instance.__dict__[i]
                setattr(instance, i, remove_html_tags(instance.__dict__[i]))
                if i in error_on_change and check != instance.__dict__[i]:
                    # only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                    raise serializers.ValidationError("html tags included in field")
            elif isinstance(instance.__dict__[i], str) and i in exclude:
                check = instance.__dict__[i]
                # even though excluded, we still check to remove script tags
                setattr(instance, i, remove_script_tags(instance.__dict__[i]))
                if i in error_on_change and check != instance.__dict__[i]:
                    # only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                    raise serializers.ValidationError("script tags included in field")
            elif (
                (isinstance(instance.__dict__[i], list) or isinstance(instance.__dict__[i], dict))
                and i in exclude
                and not any(e.startswith(i + ".") for e in exclude)
            ):
                # an excluded JSON field with no sub field rules (e.g. a form schema) keeps its html,
                # but script tags are still removed from every nested string
                instance.__dict__[i] = remove_script_tags_nested(instance.__dict__[i])
            elif (isinstance(instance.__dict__[i], list) or isinstance(instance.__dict__[i], dict)) and i in exclude:
                # if we have reached this point, it means we have a json object with fields that are allowed to contain tags
                # we'll use . notation to identify sub fields that should be carried over to the exclude and error on change lists
                # NOTE: to allow sub fields to be sanitised, the parent field should be included in both lists required for their respective children
                sub_exclude_list = list(filter(lambda e: e.startswith(i + "."), exclude))
                exclude_list = list(map(lambda e: e.replace(i + ".", "", 1), sub_exclude_list))
                # NOTE: a sub error on change list will require the parent field to be in the exclude list, to reach this point (but not necessarily in the error_on_change list)
                sub_error_on_change_list = list(filter(lambda e: e.startswith(i + "."), error_on_change))
                error_on_change_list = list(map(lambda e: e.replace(i + ".", "", 1), sub_error_on_change_list))

                if isinstance(instance.__dict__[i], dict):
                    check = instance.__dict__[i]
                    instance.__dict__[i] = sanitise_fields(
                        instance.__dict__[i],
                        exclude=exclude_list,
                        error_on_change=error_on_change_list,
                    )
                    if i in error_on_change and check != instance.__dict__[i]:
                        raise serializers.ValidationError("html tags included in field")
                elif isinstance(instance.__dict__[i], list):
                    for j in range(0, len(instance.__dict__[i])):
                        check = instance.__dict__[i][j]
                        if isinstance(instance.__dict__[i][j], str):
                            # strings in an excluded list will be treated as excluded
                            instance.__dict__[i][j] = remove_script_tags(instance.__dict__[i][j])
                        elif isinstance(instance.__dict__[i][j], list) or isinstance(instance.__dict__[i][j], dict):
                            instance.__dict__[i][j] = sanitise_fields(
                                instance.__dict__[i][j],
                                exclude=exclude_list,
                                error_on_change=error_on_change_list,
                            )
                        if i in error_on_change and check != instance.__dict__[i][j]:
                            raise serializers.ValidationError("html tags included in field")
    elif isinstance(instance, list):
        # a list directly inside a list (e.g. [["a", "b"]]) is walked by index, not as a dict
        for j in range(0, len(instance)):
            if isinstance(instance[j], str):
                instance[j] = remove_html_tags(instance[j])
            elif isinstance(instance[j], list) or isinstance(instance[j], dict):
                instance[j] = sanitise_fields(instance[j])
    else:
        remove_keys = []
        for i in instance:
            # for dicts we also check the keys - they are removed completely if not sanitary (should not change keys)
            original_key = i
            if isinstance(original_key, str):
                sanitised_key = remove_html_tags(i)
                if original_key != sanitised_key:
                    remove_keys.append(original_key)
                    continue

            # remove html tags for all string fields not in the exclude list
            if i not in exclude and (isinstance(instance[i], dict)):
                instance[i] = sanitise_fields(instance[i])

            elif isinstance(instance[i], list) and i not in exclude:
                for j in range(0, len(instance[i])):
                    check = instance[i][j]
                    if isinstance(instance[i][j], str):
                        instance[i][j] = remove_html_tags(instance[i][j])
                    elif isinstance(instance[i][j], list) or isinstance(instance[i][j], dict):
                        instance[i][j] = sanitise_fields(instance[i][j])
                    if i in error_on_change and check != instance[i][j]:
                        raise serializers.ValidationError("html tags included in field")

            else:
                if isinstance(instance[i], str) and i not in exclude:
                    check = instance[i]
                    instance[i] = remove_html_tags(instance[i])
                    if i in error_on_change and check != instance[i]:
                        # only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                        raise serializers.ValidationError("html tags included in field")
                elif isinstance(instance[i], str) and i in exclude:
                    # even though excluded, we still check to remove script tags
                    instance[i] = remove_script_tags(instance[i])
                    if i in error_on_change and check != instance[i]:
                        # only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                        raise serializers.ValidationError("script tags included in field")
                elif (isinstance(instance[i], list) or isinstance(instance[i], dict)) and i in exclude:
                    # if we have reached this point, it means we have a json object with fields that are allowed to contain tags
                    # we'll use . notation to identify sub fields that should be carried over to the exclude and error on change lists
                    # NOTE: to allow sub fields to be sanitised, the parent field should be included in both lists required for their respective children
                    sub_exclude_list = list(filter(lambda e: e.startswith(i + "."), exclude))
                    exclude_list = list(map(lambda e: e.replace(i + ".", "", 1), sub_exclude_list))
                    # NOTE: a sub error on change list will require the parent field to be in the exclude list, to reach this point (but not necessarily in the error_on_change list)
                    sub_error_on_change_list = list(filter(lambda e: e.startswith(i + "."), error_on_change))
                    error_on_change_list = list(
                        map(
                            lambda e: e.replace(i + ".", "", 1),
                            sub_error_on_change_list,
                        )
                    )

                    if isinstance(instance[i], dict):
                        check = instance[i]
                        instance[i] = sanitise_fields(
                            instance[i],
                            exclude=exclude_list,
                            error_on_change=error_on_change_list,
                        )
                        if i in error_on_change and check != instance[i]:
                            raise serializers.ValidationError("script tags included in field")
                    elif isinstance(instance[i], list):
                        for j in range(0, len(instance[i])):
                            check = instance[i][j]
                            if isinstance(instance[i][j], str):
                                # strings in an excluded list will be treated as excluded
                                instance[i][j] = remove_script_tags(instance[i][j])
                            elif isinstance(instance[i][j], list) or isinstance(instance[i][j], dict):
                                instance[i][j] = sanitise_fields(
                                    instance[i][j],
                                    exclude=exclude_list,
                                    error_on_change=error_on_change_list,
                                )
                            if i in error_on_change and check != instance[i][j]:
                                raise serializers.ValidationError("script tags included in field")

        for i in remove_keys:
            del instance[i]
    return instance


class SanitiseMixin(models.Model):
    """
    Sanitise model fields on save
    """

    def save(self, *args, **kwargs):
        # sanitise
        exclude = kwargs.pop("exclude_sanitise", [])  # fields that keep allowed html (see remove_script_tags)
        error_on_change = kwargs.pop(
            "error_on_sanitise", []
        )  # fields that should not be modified through tag removal (and should throw and error if they are)
        self = sanitise_fields(self, exclude, error_on_change)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
