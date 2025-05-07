# -*- coding: utf-8 -*-
import re
import sys
from ai_shell_assistant.assistant import main

if __name__ == '__main__':
    try:
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
