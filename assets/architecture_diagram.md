graph TB
    subgraph Input["Input"]
        Secret["Secret Number<br/>(1-100)"]
        Guess["Guess or Feedback"]
    end

    subgraph Agent["AI Agent<br/>(Agentic Workflow)"]
        Plan["PLAN<br/>Binary Search<br/>Next Guess"]
        Act["ACT<br/>Make Guess<br/>Get Feedback"]
        Learn["LEARN<br/>Update Range<br/>Compute Confidence"]
        Iterate["ITERATE<br/>Loop Until Win"]
    end

    subgraph Logic["Game Logic"]
        Check["check_guess()<br/>Compare"]
        Parse["parse_guess()<br/>Validate"]
    end

    subgraph Testing["Testing & Evaluation<br/>(Human Oversight)"]
        Tests["Automated Tests<br/>9 Test Cases"]
        Report["Reliability Report<br/>Success Rate"]
        Logs["Logging<br/>Full Decision Trail"]
    end

    subgraph Output["Output"]
        Result["Win/Loss<br/>+ Attempts"]
        Confidence["Confidence Scores<br/>+ Error Flags"]
    end

    Secret --> Act
    Guess --> Parse
    Parse --> Check
    Check --> Act
    Act --> Learn
    Learn --> Plan
    Plan --> Act
    
    Act -.->|Feedback| Tests
    Learn -.->|Confidence| Logs
    Logs -.->|Audit Trail| Tests
    Tests -.->|Validates| Report
    Report -.->|Human Reviews| Output
    
    Learn --> Result
    Learn --> Confidence
    Result --> Output
    Confidence --> Output

    style Input fill:#e3f2fd
    style Agent fill:#f3e5f5
    style Logic fill:#fff3e0
    style Testing fill:#e8f5e9
    style Output fill:#fce4ec
