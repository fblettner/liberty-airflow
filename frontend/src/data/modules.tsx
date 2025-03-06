import { EModules } from "@nomana-it/liberty-core";

export const modulesProperties = [
                { ROW_ID: 1, [EModules.id]: "menus", [EModules.description]: "Enable Drawer Menus", [EModules.enabled]: "Y", [EModules.params]: null },
                { ROW_ID: 2, [EModules.id]: "dev", [EModules.description]: "Enable Development Mode", [EModules.enabled]: "Y", [EModules.params]: null },
                { ROW_ID: 3, [EModules.id]: "grafana", [EModules.description]: "Enable Grafana Dashboard", [EModules.enabled]: "N", [EModules.params]: null },
                { ROW_ID: 4, [EModules.id]: "AI", [EModules.description]: "Enable AI", [EModules.enabled]: "Y", [EModules.params]: null },
                { ROW_ID: 5, [EModules.id]: "debug", [EModules.description]: "Enable Debug", [EModules.enabled]: "N", [EModules.params]: null },
                { ROW_ID: 6, [EModules.id]: "sentry", [EModules.description]: "Enable Sentry", [EModules.enabled]: "N", [EModules.params]: null },
                { ROW_ID: 7, [EModules.id]: "login", [EModules.description]: "Enable Embedded Login", [EModules.enabled]: "Y", [EModules.params]: null }
            ];

export const getModules = async () => {
    return modulesProperties
  };