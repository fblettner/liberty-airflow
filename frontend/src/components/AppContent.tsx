import {
  AppsContent,
  EApplications,
  useAppContext,
}
  from '@nomana-it/liberty-core';
import { useEffect } from "react";
import { currentApplication } from "@ly_data/applications";

const App = () => {

  const { appsProperties, connect } = useAppContext();
  useEffect(() => {
    // Define new application properties
    // Update state only if appsProperties are not already set
    if (!appsProperties || appsProperties[EApplications.id] !== currentApplication[EApplications.id]) {
      connect(currentApplication);
    }
  }, [appsProperties, connect]);

  return (
    <AppsContent />
  )
};

export default App;