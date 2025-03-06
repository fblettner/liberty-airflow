/*
 * Copyright (c) 2025 NOMANA-IT and/or its affiliates.
 * All rights reserved. Use is subject to license terms.
 * *
 */
import { AppProvider, LYThemeProvider } from "@nomana-it/liberty-core";
import AppContent from '@ly_components/AppContent';
import { getModules } from '@ly_data/modules';
import { getApplications } from '@ly_data/applications';
import { getToken } from '@ly_data/token';
import { getUser } from '@ly_data/user';
import { getMenus } from '@ly_data/menus';
import { theme } from '@ly_data/theme';
import { getDashboard } from '@ly_data/dashboard';
import { setLookup } from '@ly_data/lookup';
import { setEnums } from '@ly_data/enum';

export function App() {

  setLookup();
  setEnums();
  
  return (
    <AppProvider
      getModules={getModules}
      getApplications={getApplications}
      getToken={getToken}
      getUser={getUser}
      getMenus={getMenus}
      getDashboard={getDashboard}
    >
        <LYThemeProvider customTheme={theme}>
          <AppContent />
        </LYThemeProvider>
    </AppProvider>

  );
}

