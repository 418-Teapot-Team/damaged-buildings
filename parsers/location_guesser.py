import json
import os

from openai import OpenAI

client = OpenAI(
    api_key="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"
)

all_files = os.listdir("output-parsed")
for i, file in enumerate(all_files, start=1):
    filename = f"output-parsed/{file}"
    print(f"{i}/{len(all_files)}: ", filename)

    with open(filename, "r") as f:
        data = json.load(f)

    response = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        messages=[
            # {"role": "user", "content": json.dumps(data)},
            {
                "role": "user",
                "content": f"determine longitude and latitude based on the context. output just two comma separated values without any extra details. context: ```{json.dumps(data)}```",
            },
        ],
        # temperature=0,
    )

    output = response.choices[0].message.content
    assert output is not None

    # print(output)
    import re

    # Find two comma-separated floats in the output string
    match = re.search(r"(\d+\.\d+),\s*(\d+\.\d+)", output)
    if match:
        longitude, latitude = match.groups()
    else:
        # Fallback if no match found
        print("Could not find coordinates in the output")
        longitude, latitude = None, None

    data["longitude"] = longitude
    data["latitude"] = latitude

    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
