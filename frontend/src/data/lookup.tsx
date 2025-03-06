import { ELookup, GlobalSettings, ToolsDictionary } from '@nomana-it/liberty-core';

const lookupData = [{
    "columns": [
        {
            "header": "ROW_ID",
            "field": "ROW_ID",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": null,
            "rulesValues": null,
            "disabled": false,
            "required": false,
            "visible": true
        },
        {
            "header": "Component",
            "field": "COL_COMPONENT",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": "LOOKUP",
            "rulesValues": "2",
            "disabled": false,
            "required": false,
            "visible": true
        },
        {
            "header": "Lookup ID",
            "field": "LKP_ID",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": "SEQUENCE",
            "rulesValues": "15",
            "disabled": false,
            "required": false,
            "visible": true
        },
        {
            "header": "Description",
            "field": "LKP_LABEL",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": null,
            "rulesValues": null,
            "disabled": false,
            "required": false,
            "visible": true
        },
        {
            "header": "Lookup Group",
            "field": "LKP_GROUP",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": "LOOKUP",
            "rulesValues": "14",
            "disabled": false,
            "required": false,
            "visible": true
        }
    ],
    "data": [
        {
            "ROW_ID": 1,
            "COL_COMPONENT": "FormsDashboard",
            "LKP_ID": 1,
            "LKP_LABEL": "Default Dashboard",
            "LKP_GROUP": "FormsDashboard"
        }
    ],
    "header": {
        "ROW_ID": 1,
        "LKP_ID": GlobalSettings.getQuery.lookupDashboard,
        "LKP_QUERY_ID": 78,
        "LKP_DISPLAY_ADD": "N",
        "LKP_FRM_ID": null,
        "LKP_DD_ID": "LKP_ID",
        "LKP_DD_LABEL": "LKP_LABEL",
        "LKP_DD_GROUP": "LKP_GROUP",
        "LKP_DISPLAY_SEARCH": null,
        "LKP_TBL_ID": null
    },
    "status": "success"
  },
  {
    "columns": [
        {
            "header": "ROW_ID",
            "field": "ROW_ID",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": null,
            "rulesValues": null,
            "disabled": false,
            "required": false,
            "visible": true
        },
        {
            "header": "Language ID",
            "field": "LNG_ID",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": "LOOKUP",
            "rulesValues": "11",
            "disabled": false,
            "required": false,
            "visible": true
        },
        {
            "header": "Description",
            "field": "LNG_NAME",
            "type": "text",
            "operator": "like",
            "defined": false,
            "template": "text",
            "rules": null,
            "rulesValues": null,
            "disabled": false,
            "required": false,
            "visible": true
        }
    ],
    "data": [
        {
            "ROW_ID": 1,
            "LNG_ID": "en",
            "LNG_NAME": "English"
        },
        {
            "ROW_ID": 2,
            "LNG_ID": "fr",
            "LNG_NAME": "Français"
        }
    ],
    "header": {
        "ROW_ID": 1,
        "LKP_ID": GlobalSettings.getQuery.lookupLanguage,
        "LKP_QUERY_ID": 67,
        "LKP_DISPLAY_ADD": "N",
        "LKP_FRM_ID": null,
        "LKP_DD_ID": "LNG_ID",
        "LKP_DD_LABEL": "LNG_NAME",
        "LKP_DD_GROUP": null,
        "LKP_DISPLAY_SEARCH": null,
        "LKP_TBL_ID": null
    },
    "status": "success"
  },
];


export const setLookup = async () => {
  ToolsDictionary.setCustomGetLookup(async (props) => {
    const lookupContent = lookupData.find((item) => item.header[ELookup.id] === props?.[ELookup.id]);
    return lookupContent
  });
}