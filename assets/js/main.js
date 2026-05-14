$(function() {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
        const method = (options.method || options.type || '').toUpperCase();
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method) && !options.crossDomain) {
            jqXHR.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    function updateVoteUI(btn, voteType, newRating) {
        const container = btn.closest('.d-inline-flex.border');
        const divider = container.find('.border-start');
        const ratingSpan = container.find('[id*="-rating-"]');
        const upBtn = container.find('[data-type="like"]');
        const downBtn = container.find('[data-type="dislike"]');

        ratingSpan.text(newRating);

        function resetToGray() {
            container.removeClass('border-success border-danger').addClass('border-secondary');
            divider.removeClass('border-success border-danger').addClass('border-secondary');
            ratingSpan.removeClass('text-success text-danger text-secondary').addClass('text-secondary');
            upBtn.removeClass('text-success text-secondary').addClass('text-secondary');
            downBtn.removeClass('text-danger text-secondary').addClass('text-secondary');
        }

        if (voteType === 'like') {
            if (btn.hasClass('text-success')) {
                resetToGray();
            } else {
                resetToGray();
                container.removeClass('border-secondary').addClass('border-success');
                divider.removeClass('border-secondary').addClass('border-success');
                ratingSpan.removeClass('text-secondary').addClass('text-success');
                btn.removeClass('text-secondary').addClass('text-success');
            }
        } else if (voteType === 'dislike') {
            if (btn.hasClass('text-danger')) {
                resetToGray();
            } else {
                resetToGray();
                container.removeClass('border-secondary').addClass('border-danger');
                divider.removeClass('border-secondary').addClass('border-danger');
                ratingSpan.removeClass('text-secondary').addClass('text-danger');
                btn.removeClass('text-secondary').addClass('text-danger');
            }
        }
    }

    $(document).on('click', '.question-vote', function(e) {
        e.preventDefault();
        const btn = $(this);
        const questionId = btn.data('id');
        const voteType = btn.data('type');

        $.ajax({
            url: '/ajax/like-question/',
            method: 'POST',
            data: {
                'question_id': questionId,
                'type': voteType
            }
        })
        .done(function(response) {
            updateVoteUI(btn, voteType, response.rating);
        })
        .fail(function(xhr) {
            if (xhr.status === 401) {
                window.location.href = '/login/';
            } else {
                alert(xhr.responseJSON?.error || "Произошла ошибка");
            }
        });
    });

    $(document).on('click', '.answer-vote', function(e) {
        e.preventDefault();
        const btn = $(this);
        const answerId = btn.data('id');
        const voteType = btn.data('type');

        $.ajax({
            url: '/ajax/like-answer/',
            method: 'POST',
            data: {
                'answer_id': answerId,
                'type': voteType
            }
        })
        .done(function(response) {
            updateVoteUI(btn, voteType, response.rating);
        })
        .fail(function(xhr) {
            if (xhr.status === 401) {
                window.location.href = '/login/';
            } else {
                alert(xhr.responseJSON?.error || "Произошла ошибка");
            }
        });
    });

    $(document).on('click', '.correct-answer-btn', function(e) {
        e.preventDefault();
        const btn = $(this);
        const questionId = btn.data('question-id');
        const answerId = btn.data('answer-id');

        $.ajax({
            url: '/ajax/mark-correct/',
            method: 'POST',
            data: {
                'question_id': questionId,
                'answer_id': answerId
            }
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
            if (xhr.status === 401) {
                window.location.href = '/login/';
            } else if (xhr.status === 403) {
                alert("Только автор вопроса может отмечать правильный ответ!");
            } else {
                alert(xhr.responseJSON?.error || "Произошла ошибка");
            }
        });
    });
});
