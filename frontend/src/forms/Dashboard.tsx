import { Card, CardContent, Div_DialogWidgetContent, MarkDown } from '@nomana-it/liberty-core';

const markDownPreview = `
# Liberty Airflow

A Scalable and Extensible FastAPI and React Scheduler prebuilt with Airflow
`;

const markdownContent = `
## Prebuilt Dags

### **Daily DAGs**
- **\`airflow-purge-daily-1\`**: Purges old Airflow logs and metadata on a daily schedule (\`@daily\`).
- **\`database-backup-daily-1\`**: Backs up databases every day at 01:00 AM (\`00 1 * * *\`).

### **Weekly DAGs**
- **\`database-purge-weekly-1\`**: Performs database cleanup and purging on a weekly schedule (\`@weekly\`).

### **Unscheduled DAGs**
- **\`airflow-sync-1\`**: Synchronizes repositories as needed (manually triggered).

`;

export const Core_Home = () => {
  return (

      <Div_DialogWidgetContent>
        <Card>
          <CardContent>
            {/* Render markdown documentation */}
            <MarkDown markdown={markDownPreview} />
          </CardContent>

          <CardContent>
            {/* Render markdown documentation */}
            <MarkDown markdown={markdownContent} />
          </CardContent>
        </Card>
      </Div_DialogWidgetContent>

  );
};