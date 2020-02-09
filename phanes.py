from os import remove
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
        save_handle = BytesIO(files[save_name])
    except KeyError:
        raise KeyError("Could not find save file {}".format(save_name))

    tree = etree.parse(save_handle)

    entries = tree.xpath(
        "/GameSave/m_entityListHiringManager/m_entities/EntitySave"
    )

    for entity in entries:
        # Component system:type="EmployeeComponentPersistentData"
        skillsets = entity.xpath(
            "Components/Component[@system:type='EmployeeComponentPersistentData']/m_skillSet",
            namespaces={
                "system": "http://www.w3.org/2001/XMLSchema-instance"
            }
        )

        for skillset in skillsets:
            skills = skillset.xpath("m_qualifications/Skill/m_level|m_specialization1/m_level|m_specialization2/m_level")

            for skill in skills:
                skill.text = "{}".format(5)

    tree.write(save_handle)

    files[save_name] = save_handle.getbuffer()

remove(filename)

with ZipFile(filename, mode="w") as zip_file:
    for filename, contents in files.items():
        zip_file.writestr(filename, contents)
