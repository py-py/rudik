django.jQuery(document).ready(function () {
    const selector = '.field-is_default input[type="checkbox"]';
    django.jQuery(selector).on('click', function () {
        django.jQuery(selector).not(this).prop('checked', false);
    });
});