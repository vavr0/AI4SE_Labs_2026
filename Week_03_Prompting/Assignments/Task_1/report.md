# Task 1 — Prompting Frameworks

## RTF — Role, Task, Format

Source: https://frompting.com/frameworks/rtf

I chose RTF because it is compact and clearly states the model's role, the operation to perform and the required output format. I expect it to produce consistently formatted SQL predictions with less unwanted commentary. Its simplicity may leave more interpretation to the model than a more detailed structure.

## ICIO — Instruction, Context, Input, Output

Source: https://frompting.com/frameworks/icio

I chose ICIO because it separates the instructions, database schema, question dataset and output requirements. This fits a task that transforms supplied input into machine-readable output. I expect this separation to reduce ambiguity about which information to use and what to return.

## APE — Action, Purpose, Expectation

Source: https://frompting.com/frameworks/ape

I chose APE to investigate whether explaining the purpose of the generated queries helps the model stay focused on accurate restaurant retrieval and automatic evaluation. I expect the explicit purpose and expectations to support task adherence, but they may provide little benefit over the simpler RTF prompt.
