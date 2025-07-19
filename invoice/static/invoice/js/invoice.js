$(document).ready(function () {
    $('#payModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var invoiceId = button.data('id');
        $('#invoiceId').val(invoiceId);
    });

    $('#paymentForm').on('submit', function (e) {
        e.preventDefault();
        var invoiceId = $('#invoiceId').val();
        var amount = $('#paymentAmount').val();
        $.ajax({
            url: `/api/invoices/${invoiceId}/pay/`,
            method: 'POST',
            data: { amount: amount },
            headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
            success: function () {
                location.reload();
            },
            error: function (xhr) {
                alert('Payment failed: ' + xhr.responseJSON.error);
            }
        });
    });

    $(document).on('click', '.cancel-btn', function () {
        var invoiceId = $(this).data('id');
        if (confirm("Cancel this invoice?")) {
            $.ajax({
                url: `/api/invoices/${invoiceId}/cancel/`,
                method: 'POST',
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                success: function () {
                    location.reload();
                },
                error: function (xhr) {
                    alert('Cancel failed: ' + xhr.responseJSON.error);
                }
            });
        }
    });
});
