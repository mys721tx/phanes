from zipfile import ZipFile
from pathlib import Path
from io import BytesIO


from lxml import etree

filename = "test.zip"

with ZipFile(filename) as zip_file:
    files = {
        name: zip_file.read(name) for name in zip_file.namelist()
    }

    save_name = "{}.xml".format(Path(filename).stem)

    try:
        tree = etree.parse(BytesIO(files[save_name]))
    except KeyError:
        raise KeyError("Could not find save file {}".format(save_name))

    entries = tree.xpath(
        "/GameSave/m_entityListHiringManager/m_entities/EntitySave"
    )

    for entity in entries:
        # Component system:type="EmployeeComponentPersistentData"
        skills = entity.xpath(
            "Components/Component[@system:type='EmployeeComponentPersistentData']/m_skillSet",
            namespaces={
                "system": "http://www.w3.org/2001/XMLSchema-instance"
            }
        )

        print(len(skills))
