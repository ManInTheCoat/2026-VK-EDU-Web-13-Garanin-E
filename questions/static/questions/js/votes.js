$(function() {
    function showErrorToast(message) {
        $('.custom-error-toast').remove();

        const toast = $(`
            <div class="custom-error-toast position-fixed bottom-0 end-0 p-4" style="z-index: 1080;">
                <div class="toast align-items-center text-white bg-danger border-0 show shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body fs-6">
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            </div>
        `);

        $('body').append(toast);

        toast.find('.btn-close').on('click', function() {
            toast.fadeOut(300, function() { $(this).remove(); });
        });

        setTimeout(function() {
            toast.fadeOut(300, function() { $(this).remove(); });
        }, 4000);
    }

    function updateVoteUI(btn, serverVoteState, newRating) {
        const container = btn.closest('.vote-container');
        const divider = container.find('.vote-controls');
        const ratingSpan = container.find('[id*="-rating-"]');
        const upBtn = container.find('[data-type="like"]');
        const downBtn = container.find('[data-type="dislike"]');

        ratingSpan.text(newRating);

        container.removeClass('border-success border-danger').addClass('border-secondary');
        divider.removeClass('border-success border-danger').addClass('border-secondary');
        ratingSpan.removeClass('text-success text-danger text-secondary').addClass('text-secondary');
        upBtn.removeClass('text-success text-secondary').addClass('text-secondary');
        downBtn.removeClass('text-danger text-secondary').addClass('text-secondary');

        if (serverVoteState === 'like') {
            container.removeClass('border-secondary').addClass('border-success');
            divider.removeClass('border-secondary').addClass('border-success');
            ratingSpan.removeClass('text-secondary').addClass('text-success');
            upBtn.removeClass('text-secondary').addClass('text-success');
        } else if (serverVoteState === 'dislike') {
            container.removeClass('border-secondary').addClass('border-danger');
            divider.removeClass('border-secondary').addClass('border-danger');
            ratingSpan.removeClass('text-secondary').addClass('text-danger');
            downBtn.removeClass('text-secondary').addClass('text-danger');
        }
    }

    $(document).on('click', '.question-vote', function(e) {
        e.preventDefault();
        const btn = $(this);

        if (btn.prop('disabled')) return;

        btn.prop('disabled', true).css('pointer-events', 'none');

        const questionId = btn.data('id');
        const voteType = btn.data('type');

        $.ajax({
            url: `/ajax/question/${questionId}/like/`,
            method: 'POST',
            data: { 'type': voteType }
        })
        .done(function(response) {
            updateVoteUI(btn, response.vote, response.rating);
        })
        .fail(function(xhr) {
            if (xhr.status === 401) window.location.href = '/core/login/';
            else showErrorToast(xhr.responseJSON?.error || "Произошла ошибка");
        })
        .always(function() {
            btn.prop('disabled', false).css('pointer-events', '');
        });
    });

    $(document).on('click', '.answer-vote', function(e) {
        e.preventDefault();
        const btn = $(this);

        if (btn.prop('disabled')) return;
        btn.prop('disabled', true).css('pointer-events', 'none');

        const answerId = btn.data('id');
        const voteType = btn.data('type');

        $.ajax({
            url: `/ajax/answer/${answerId}/like/`,
            method: 'POST',
            data: { 'type': voteType }
        })
        .done(function(response) {
            updateVoteUI(btn, response.vote, response.rating);
        })
        .fail(function(xhr) {
            if (xhr.status === 401) window.location.href = '/core/login/';
            else showErrorToast(xhr.responseJSON?.error || "Произошла ошибка");
        })
        .always(function() {
            btn.prop('disabled', false).css('pointer-events', '');
        });
    });

    $(document).on('click', '.correct-answer-btn', function(e) {
        e.preventDefault();
        const btn = $(this);

        if (btn.prop('disabled')) return;
        btn.prop('disabled', true).css('pointer-events', 'none');

        const questionId = btn.data('question-id');
        const answerId = btn.data('answer-id');

        $.ajax({
            url: `/ajax/question/${questionId}/answer/${answerId}/correct/`,
            method: 'POST',
        })
        .done(function(response) {
            const allBtns = $('.correct-answer-btn[data-question-id="' + questionId + '"]');
            allBtns.removeClass('text-success').addClass('text-secondary');
            allBtns.attr('title', 'Mark as correct answer');
            allBtns.find('.btn-text').text('Mark as Accepted');

            if (response.is_correct) {
                btn.removeClass('text-secondary').addClass('text-success');
                btn.attr('title', 'Unmark as correct answer');
                btn.find('.btn-text').text('Accepted answer');
            }
        })
        .fail(function(xhr) {
            if (xhr.status === 401) window.location.href = '/core/login/';
            else showErrorToast(xhr.responseJSON?.error || "Произошла ошибка");
        })
        .always(function() {
            btn.prop('disabled', false).css('pointer-events', '');
        });
    });
});
