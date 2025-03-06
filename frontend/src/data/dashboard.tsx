import { LYComponentType } from '@nomana-it/liberty-core';
import { Core_Home } from "../forms/Dashboard";

export const dashboard = [{ 
    "header": {
        "DSH_ID": 1,
        "DSH_LABEL": "Default Dashboard",
        "DSH_ROW": 1,
        "DSH_COLUMN": 1
    },
    "content": [
        {
            "DSH_ID": 1,
            "DSH_COL_ID": 1,
            "DSH_DISPLAY_TITLE": "N",
            "DSH_TITLE": "Documentation",
            "DSH_ROW": 1,
            "DSH_COLUMN": 1,
            "DSH_COMPONENT": LYComponentType.FormsContent,
            "DSH_COMPONENT_ID": null,
            "DSH_CONTENT": <Core_Home />
        }
    ],
    "status": "success"
}
]

export const getDashboard = async (dashboard_id: Number) => {
    const current_dashboard = dashboard.find((dashboard: any) => dashboard.header.DSH_ID === dashboard_id)
    return current_dashboard
  };
