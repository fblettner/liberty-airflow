import { user } from "@ly_data/user";

export const token_successful = {
    "access_token": "123456",
    "token_type": "bearer",
    "status": "success",
    "message": "Authentication successful"
};

export const token_login_failed = {
    "access_token": "",
    "token_type": "bearer",
    "status": "failed",
    "message": "loginError"
};

export const token_password_failed = {
    "access_token": "",
    "token_type": "bearer",
    "status": "failed",
    "message": "passwordError"
};

export const getToken = async (user_id: string, password: string) => {
    const isLogin = user.some((user) => user.USR_ID === user_id);
    const isPassword = user.some((user) => user.USR_PASSWORD === password);

    if (!isLogin) return token_login_failed;
    if (!isPassword) return token_password_failed;

    return token_successful
  };

