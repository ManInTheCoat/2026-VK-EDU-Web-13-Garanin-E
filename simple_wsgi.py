import urllib.parse

def application(environ, start_response):
    """
    Простой WSGI-скрипт без использования Django.
    Выводит переданные GET и POST параметры.
    """

    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    query_string = environ.get('QUERY_STRING', '')
    get_params = urllib.parse.parse_qsl(query_string)

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    post_params = urllib.parse.parse_qsl(request_body)

    response_lines = ["=== Simple WSGI Script ===\n"]

    response_lines.append("[GET Parameters]")
    if get_params:
        for key, value in get_params:
            response_lines.append(f"{key}: {value}")
    else:
        response_lines.append("No GET parameters")

    response_lines.append("\n[POST Parameters]")
    if post_params:
        for key, value in post_params:
            response_lines.append(f"{key}: {value}")
    else:
        response_lines.append("No POST parameters")

    response_text = "\n".join(response_lines)

    return [response_text.encode('utf-8')]
