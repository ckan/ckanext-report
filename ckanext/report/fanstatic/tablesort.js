$(document).ready(function()
{
    $("#report-table").tablesorter({
        dateFormat: "uk",
    });
    $(".js-auto-submit").change(function () {
        $(this).closest("form").submit();
    });
}
);

