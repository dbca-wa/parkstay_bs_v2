from django.conf import settings
from django.contrib.gis.forms import OSMWidget


class KBMapWidget(OSMWidget):
    """
    Map widget for the Django admin with the Kaartdijin Boodja streets tiles as background,
    instead of the OpenStreetMap tiles of OSMWidget (blocked by the OSM tile servers).
    """
    template_name = "ps/admin/openlayers-kb.html"
    # Western Australia, shown when the object has no point yet
    default_lon = 122
    default_lat = -26
    default_zoom = 5

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["streets_url"] = settings.MAP_STREETS_URL
        context["streets_layer"] = settings.MAP_STREETS_LAYER
        return context
