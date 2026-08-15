#!/usr/bin/env python3
"""Build the unsigned PanoViewer share-sheet shortcut.

Sign the result on macOS with:
  shortcuts sign --mode anyone --input dist/PanoViewer-unsigned.shortcut \
    --output shortcuts/PanoViewer.shortcut
"""

from __future__ import annotations

import plistlib
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist" / "PanoViewer-unsigned.shortcut"
TEMPLATE_URL = (
    "https://github.com/liang-xiaohui/PanoViewer/releases/latest/download/"
    "PanoViewer-Template.html"
)


def uid() -> str:
    return str(uuid4()).upper()


def attachment(value: dict) -> dict:
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def action_output(action_id: str, name: str) -> dict:
    return attachment({"OutputUUID": action_id, "Type": "ActionOutput", "OutputName": name})


def token_string(text: str, attachments: dict[str, dict] | None = None) -> dict:
    value: dict = {"string": text}
    if attachments:
        value["attachmentsByRange"] = attachments
    return {"Value": value, "WFSerializationType": "WFTextTokenString"}


def build() -> dict:
    convert_id, image_b64_id, download_id = (uid() for _ in range(3))
    replace_id, html_file_id = (uid() for _ in range(2))

    shortcut_input = attachment({"Type": "ExtensionInput"})
    actions = [
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.image.convert",
            "WFWorkflowActionParameters": {
                "UUID": convert_id,
                "WFInput": shortcut_input,
                "WFImageFormat": "JPEG",
                "WFImageCompressionQuality": 1.0,
                "WFImagePreserveMetadata": False,
            },
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.base64encode",
            "WFWorkflowActionParameters": {
                "UUID": image_b64_id,
                "WFInput": action_output(convert_id, "Converted Image"),
                "WFEncodeMode": "Encode",
                "WFBase64LineBreakMode": "None",
            },
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
            "WFWorkflowActionParameters": {
                "UUID": download_id,
                "WFURL": TEMPLATE_URL,
                "WFHTTPMethod": "GET",
            },
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.text.replace",
            "WFWorkflowActionParameters": {
                "UUID": replace_id,
                "WFInput": action_output(download_id, "Contents of URL"),
                "WFReplaceTextFind": "__EMBEDDED_IMAGE__",
                "WFReplaceTextReplace": token_string(
                    "data:image/jpeg;base64,\ufffc",
                    {
                        "{23, 1}": {
                            "OutputUUID": image_b64_id,
                            "Type": "ActionOutput",
                            "OutputName": "Base64 Encoded",
                        }
                    },
                ),
                "WFReplaceTextCaseSensitive": True,
                "WFReplaceTextRegularExpression": False,
            },
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setitemname",
            "WFWorkflowActionParameters": {
                "UUID": html_file_id,
                "WFInput": action_output(replace_id, "Updated Text"),
                "WFName": "PanoViewer.html",
                "WFDontIncludeFileExtension": False,
            },
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.showwebpage",
            "WFWorkflowActionParameters": {
                "WFURL": action_output(html_file_id, "Renamed Item"),
                "WFEnterSafariReader": False,
            },
        },
    ]

    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientRelease": "6.0",
        "WFWorkflowClientVersion": "3000",
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": 59511,
            "WFWorkflowIconStartColor": 431817727,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": ["WFImageContentItem"],
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowTypes": ["ActionExtension"],
        "WFWorkflowHasShortcutInputVariables": True,
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowNoInputBehavior": {
            "Name": "WFWorkflowNoInputBehaviorAskForInput",
            "Parameters": {"ItemClass": "WFImageContentItem"},
        },
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("wb") as output:
        plistlib.dump(build(), output, fmt=plistlib.FMT_BINARY, sort_keys=False)
    print(OUTPUT)


if __name__ == "__main__":
    main()
