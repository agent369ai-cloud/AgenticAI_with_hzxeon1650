System Design View
User Input
   ↓
LangGraph (State Machine)
   ↓
LLM (llama3)
   ↓
Tool Selector Node
   ↓
Calculator Tool (Python)
   ↓
Response Formatter


#LLM → detects math → calls tool → tool returns 110 → LLM formats

calculator-agent/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                # entry point
│   ├── config.py              # env + settings
│   │
│   ├── llm/
│   │   └── ollama_client.py  # LLM wrapper
│   │
│   ├── graph/
│   │   ├── builder.py        # LangGraph build
│   │   ├── nodes.py          # LLM + tool nodes
│   │   └── router.py         # decision logic
│   │
│   ├── tools/
│   │   └── calculator.py     # tool implementation
│   │
│   ├── utils/
│   │   ├── parser.py         # expression extraction
│   │   └── logger.py
│   │
│   └── schemas/
│       └── state.py          # graph state schema
│
├── tests/
│   └── test_calculator.py
│
├── requirements.txt
├── .env
├── run.py                    # CLI runner
└── README.md


###########################################################  GenAI App Flow ######################
User → run.py → main.py
                  ↓
             LangGraph (builder)
                  ↓
      nodes (LLM / tool execution)
                  ↓
          tools (calculator)
