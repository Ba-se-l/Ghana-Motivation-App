
# هاد الخطا طلع لما ستخدمنا نقطة النهاية (users/status)

```bash
INFO:     127.0.0.1:51461 - "GET /api/v1/users/status HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 416, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 63, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\applications.py", line 1163, in __call__
    await super().__call__(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\applications.py", line 96, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\middleware\cors.py", line 88, in __call__
    await self.app(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\routing.py", line 670, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 2734, in app
    await route.handle(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 1780, in handle
    await self.original_router.handle(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 2789, in handle
    await included_router._handle_selected(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 1791, in _handle_selected
    await route.handle(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 1780, in handle
    await self.original_router.handle(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 2789, in handle
    await included_router._handle_selected(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 1800, in _handle_selected
    await original_route.handle(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 1279, in handle
    await app(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 158, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 144, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 706, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\.venv\Lib\site-packages\fastapi\routing.py", line 352, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\GhanaMotivationApp\modules\user\router.py", line 44, in get_status
    return await service.get_user_status(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\GhanaMotivationApp\modules\user\service.py", line 207, in get_user_status
    trial_remaining = _calculate_trial_remaining_seconds(trial_end=user.trial_end)
  File "D:\_Python Projects-27-05-2026\ghana-motivation-backend\GhanaMotivationApp\modules\user\service.py", line 52, in _calculate_trial_remaining_seconds
    delta = trial_end - now
            ~~~~~~~~~~^~~~~
TypeError: can't subtract offset-naive and offset-aware datetimes
```