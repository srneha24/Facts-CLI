from auth import get_local_token, get_user_by_token

def restore_session():
    token = get_local_token()
    if not token:
        return None
    user = get_user_by_token(token)
    if not user:
        return None
    return {"token": token, "username": user.username}
