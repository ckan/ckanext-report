$(document).ready(function()
    {
        $(".js-auto-submit").change(function () {
            console.log('foo')
            $(this).closest("form").submit();
        });
    }
);
