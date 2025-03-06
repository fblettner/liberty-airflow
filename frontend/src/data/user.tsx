import { EUsers, IUsersProps, UIDisplayMode } from '@nomana-it/liberty-core';

export const user = [
        {
            "USR_ID": "admin",
            "USR_PASSWORD": "admin",
            "USR_NAME": "Administrator",
            "USR_EMAIL": "admin@liberty.fr",
            "USR_STATUS": "Y",
            "USR_ADMIN": "Y",
            "USR_LANGUAGE": "en",
            "USR_MODE": "dark",
            "USR_READONLY": "N",
            "USR_DASHBOARD": 1,
            "USR_THEME": "liberty"
        },
        {
            "USR_ID": "demo",
            "USR_PASSWORD": "demo",
            "USR_NAME": "Demo User",
            "USR_EMAIL": "demo@liberty.fr",
            "USR_STATUS": "Y",
            "USR_ADMIN": "Y",
            "USR_LANGUAGE": "en",
            "USR_MODE": "dark",
            "USR_READONLY": "N",
            "USR_DASHBOARD": 1,
            "USR_THEME": "liberty"
        }
    ]

export const getUser = async (user_id: string) => {
    const current_user = user.find((user: any) => user.USR_ID === user_id)
    if (current_user === undefined) {
        return {
            "items" : [],
            "status": "failed",
        }
    }
    else 
        return {
            "items": [current_user],
            "status": "success",
        }
  };

export const currentUser: IUsersProps = {
    [EUsers.status]: true,
    [EUsers.id]: "demo",
    [EUsers.name]: "Demo User",
    [EUsers.email]: "demo@liberty.fr",
    [EUsers.password]: "",
    [EUsers.admin]: "Y",
    [EUsers.language]: "en",
    [EUsers.displayMode]: UIDisplayMode.dark,
    [EUsers.darkMode]: true,
    [EUsers.readonly]: "N",
    [EUsers.dashboard]: undefined,
    [EUsers.theme]: "liberty"
    };