from os import remove
from zipfile import ZipFile
from pathlib import Path
from io import BytesIO

from lxml import etree

filename = "test.zip"

TRAITS = [
    "PERK_CHEMIST",
    "PERK_CLEAN_FEET",
    "PERK_COMFORTING",
    "PERK_DIAGNOSTIC_GENIUS",
    "PERK_FAST",
    "PERK_FAST_LEARNER",
    "PERK_GOOD_BOSS",
    "PERK_HARD_WORKER",
    "PERK_LOYAL",
    "PERK_PEOPLE_PERSON",
    "PERK_PLEASANT",
    "PERK_PRACTICAL_DIAGNOSES",
    "PERK_RESTZISTANCE",
    "PERK_SCHOLAR",
    "PERK_SPARTAN"
]

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
        "/GameSave/m_floorPersistentData/FloorPersistentData/m_entityList/m_entities/EntitySave"
    )

    for entity in entries:
        # Component system:type="EmployeeComponentPersistentData"
        employees = entity.xpath(
            "Components/Component[@system:type='EmployeeComponentPersistentData']",
            namespaces={
                "system": "http://www.w3.org/2001/XMLSchema-instance"
            }
        )

        for employee in employees:

            salaries = employee.xpath("m_salary")

            for salary in salaries:
                salary.text = "{}".format(0)

            salaries_hired = employee.xpath("m_hiredSalaryRandomization")

            for salary in salaries_hired:
                salary.text = "{}".format(0)

            levels = employee.xpath("m_level")

            for level in levels:
                level.text = "{}".format(2)

            levels_hired = employee.xpath("m_hiredLevel")

            for level in levels_hired:
                level.text = "{}".format(1)

            flags_levelup = employee.xpath("m_leveledUpAfterHire")

            for flag in flags_levelup:
                flag.text = "true"

            skillsets = employee.xpath("m_skillSet")

            for skillset in skillsets:
                skills = skillset.xpath(
                    "m_qualifications/Skill/m_level|m_specialization1/m_level|m_specialization2/m_level"
                )

                for skill in skills:
                    skill.text = "{}".format(5)

        perksets = entity.xpath(
            "Components/Component[@system:type='PerkSet']/m_perks",
            namespaces={
                "system": "http://www.w3.org/2001/XMLSchema-instance"
            }
        )

        for perkset in perksets:

            for child in perkset.iterchildren():
                perkset.remove(child)

            for trait in TRAITS:
                perk = etree.SubElement(perkset, "Perk")
                m_perk = etree.SubElement(perk, "m_perk")
                pointer = etree.SubElement(m_perk, "GameDBPointer", ID=trait)

                m_hidden = etree.SubElement(perk, "m_hidden")
                m_hidden.text = "false"

        infos_char = entity.xpath(
            "Components/Component[@system:type='CharacterPersonalInfo']",
            namespaces={
                "system": "http://www.w3.org/2001/XMLSchema-instance"
            }
        )

        for info in infos_char:
            ages = info.xpath("m_age")

            for age in ages:
                age.text = "{}".format(23)

            cats_age = info.xpath("m_ageCategory/GameDBPointer")

            for cat_age in cats_age:
                cat_age.attrib["ID"] = "AGE_YOUNG"

    out_handle = BytesIO()

    tree.write(out_handle, xml_declaration=True, encoding="utf-8")

    files[save_name] = out_handle.getbuffer()

remove(filename)

with ZipFile(filename, mode="w") as zip_file:
    for filename, contents in files.items():
        zip_file.writestr(filename, contents)
