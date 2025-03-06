import { EApplications, ESessionMode, IAppsProps } from '@nomana-it/liberty-core';

export const appsProperties = {
    "items": [
        {
            "ROW_ID": 1,
            "APPS_ID": 1,
            "APPS_NAME": "Liberty Airflow",
            "APPS_DESCRIPTION": "Liberty Airflow",
            "APPS_POOL": "default",
            "APPS_OFFSET": 5000,
            "APPS_LIMIT": 10000,
            "APPS_VERSION": 500,
            "APPS_DASHBOARD": 1,
            "APPS_THEME": "liberty"
        }
    ],
    "status": "success",

};

export const getApplications = async () => {
    return appsProperties
  };

export const currentApplication: IAppsProps = {
      [EApplications.id]: 1,
      [EApplications.pool]: "default",
      [EApplications.name]: "Liberty Airflow",
      [EApplications.description]: "Liberty Airflow",
      [EApplications.offset]: 5000,
      [EApplications.limit]: 10000,
      [EApplications.version]: "600",
      [EApplications.session]: ESessionMode.session,
      [EApplications.dashboard]: 1,
      [EApplications.theme]: "liberty",
      [EApplications.jwt_token]: "",
    };