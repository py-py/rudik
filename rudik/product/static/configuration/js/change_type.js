django.jQuery(document).ready(function () {
    const typeField = django.jQuery("#id_type");
    const url = typeField.data().url;
    const valueField = django.jQuery("#id_value");

    function changeType() {
        django.jQuery.getJSON(url, {"type_id": typeField.val()}, function (data) {
            valueField.prop("type", data.isColor ?  "color": "text");
        })
    }

    changeType();
    typeField.on('change', changeType);
});