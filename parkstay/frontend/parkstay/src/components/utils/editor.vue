<template lang="html" id="editor">
    <div class="row" style="margin-top: 40px;">
        <div class="col-md-12">
            <div class="form-group">
                <slot name="label">
                    <label class="control-label">Description</label>
                </slot>
                <div :id="editor_id" class="form-control editor"></div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    $,
}
    from '../../hooks.js'
import "quill/dist/quill.snow.css";
import Editor from 'quill';
import { onMounted, ref } from 'vue';

const model = defineModel()
const emit = defineEmits(['input']);

let editor = null
const editor_id = 'editor' + crypto.randomUUID();

const disabled = function (is_disabled) {
    editor.enable(!is_disabled);
}
const updateContent = function (content) {
    editor.setText('');
    editor.clipboard.dangerouslyPasteHTML(0, content, 'api');
    emit('input', content);
}

defineExpose({ disabled, updateContent, editor_id })

onMounted(function () {
    editor = new Editor('#' + editor_id, {
        modules: {
            toolbar: true
        },

        theme: 'snow'
    });
    editor.on('text-change', function (delta, oldDelta, source) {
        var text = $('#' + editor_id + ' >.ql-editor').html();
        // emit('input', text);
        model.value = text
    });
    var valueReady = setInterval(function () {
        if (typeof model.value != "undefined") {
            editor.clipboard.dangerouslyPasteHTML(0, model.value, 'api');
            clearInterval(valueReady);
        }
    }, 100);

})
</script>

<style lang="css" scoped>
.editor {
    height: 200px;
}
</style>
