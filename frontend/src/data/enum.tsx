import { EEnumHeader, GlobalSettings, ToolsDictionary } from '@nomana-it/liberty-core';

  const enumData = [{
    columns: [
      { header: "Enum ID", field: "ENUM_ID" },
      { header: "Value", field: "VAL_ENUM" },
      { header: "Description", field: "VAL_LABEL" }
    ],
    data: [
      { VAL_ENUM: "liberty", VAL_LABEL: "Liberty Theme" },
      { VAL_ENUM: "boldRedBlack", VAL_LABEL: "Bold Red & Black: Bold and energetic red with sleek black accents." },
      { VAL_ENUM: "luxuryDarkGold", VAL_LABEL: "Luxury Dark & Gold: Elegant gold and grey for luxury brands." }
    ],
    header: {
      ENUM_ID: GlobalSettings.getQuery.enumTheme,
      ENUM_LABEL: "Custom Dictionary",
      ENUM_DISPLAY_ADD: "Y"
    },
    status: "success"
  }];


export const setEnums = async () => {
  ToolsDictionary.setCustomGetEnums(async (props) => {
    const enumContent = enumData.find((item) => item.header[EEnumHeader.id] === props?.[EEnumHeader.id]);
    return enumContent
  });
}