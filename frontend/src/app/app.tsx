/*
 * Copyright (c) 2025 NOMANA-IT and/or its affiliates.
 * All rights reserved. Use is subject to license terms.
 * *
 */
import { AppProvider, AppsContent, LYThemeProvider } from "@nomana-it/liberty-core";
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
      getMenus={getMenus}
      getDashboard={getDashboard}
    >
        <LYThemeProvider customTheme={theme}>
          <AppsContent />
        </LYThemeProvider>
    </AppProvider>

  );
}

