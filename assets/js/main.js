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
});
