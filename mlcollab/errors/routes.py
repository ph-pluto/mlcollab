from flask import Blueprint, render_template

error = Blueprint('error', __name__)

@error.app_errorhandler(401)
def error_401(message):
    return render_template('error/errors.html', message=message, code=401), 401


@error.app_errorhandler(403)
def error_403(message):
    return render_template('error/errors.html', message=message, code=403), 403


@error.app_errorhandler(404)
def error_404(message):
    return render_template('error/errors.html', message=message, code=404), 404


@error.app_errorhandler(405)
def error_405(message):
    return render_template('error/errors.html', message=message, code=405), 405


@error.app_errorhandler(500)
def error_500(message):
    return render_template('error/errors.html', message=message, code=500), 500


@error.app_errorhandler(503)
def error_503(message):
    return render_template('error/errors.html', message=message, code=503), 503


@error.app_errorhandler(505)
def error_505(message):
    return render_template('error/errors.html', message=message, code=505), 505
