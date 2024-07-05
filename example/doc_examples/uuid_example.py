from uuid import UUID

import platitudes as pl


def read_uuid(some_uuid: UUID):
    print(f"Your uuid is: {some_uuid}")
    print(f"Version {some_uuid.version}")


pl.run(read_uuid)
