from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

{
  "provider": "autogen_agentchat.teams.RoundRobinGroupChat",
  "component_type": "team",
  "version": 1,
  "component_version": 1,
  "label": "multi-agent-system",
  "config": {
    "participants": [
      {
        "provider": "autogen_agentchat.agents.AssistantAgent",
        "component_type": "agent",
        "version": 1,
        "component_version": 1,
        "label": "Researcher",
        "config": {
          "name": "Researcher",
          "description": "Agent that performs detailed research on a given topic.",
          "system_message": "You are a research assistant. Provide a detailed, factual explanation of the topic: {topic}. Use academic and web sources. Focus on key points, data, and insights.",
          "model": "gpt-4",
          "model_client": {
            "provider": "autogen_ext.models.openai.OpenAIChatCompletionClient",
            "component_type": "model",
            "version": 1,
            "component_version": 1,
            "description": "OpenAI GPT-4o-mini",
            "label": "New Model",
            "config": {
              "model": "mistralai/mistral-7b-instruct",
              "base_url": "https://openrouter.ai/api/v1",
              "api_key": os.getenv("OPENROUTER_API_KEY"),
            }
          },
          "reflect_on_tool_use": false,
          "tool_call_summary_format": "simple"
        }
      },
      {
        "provider": "autogen_agentchat.agents.AssistantAgent",
        "component_type": "agent",
        "version": 1,
        "component_version": 1,
        "label": "Summarizer",
        "config": {
          "name": "Summarizer",
          "description": "Agent that summarizes research content into bullet points.",
          "system_message": "You are a summarizer bot. Summarize the following content in concise bullet points: {text}.",
          "model": "gpt-4",
          "model_client": {
            "provider": "autogen_ext.models.openai.OpenAIChatCompletionClient",
            "component_type": "model",
            "version": 1,
            "component_version": 1,
            "description": "OpenAI GPT-4o-mini",
            "label": "New Model",
            "config": {
              "model": "mistralai/mistral-7b-instruct",
              "base_url": "https://openrouter.ai/api/v1",
              "api_key": os.getenv("OPENROUTER_API_KEY")
            }
          },
          "reflect_on_tool_use": false,
          "tool_call_summary_format": "simple"
        }
      },
      {
        "provider": "autogen_agentchat.agents.AssistantAgent",
        "component_type": "agent",
        "version": 1,
        "component_version": 1,
        "label": "Notifier",
        "config": {
          "name": "Notifier",
          "description": "Agent that presents the final summary to the user.",
          "system_message": "You are a notifier. Present the following summary clearly to the user.",
          "model": "gpt-4",
          "model_client": {
            "provider": "autogen_ext.models.openai.OpenAIChatCompletionClient",
            "component_type": "model",
            "version": 1,
            "component_version": 1,
            "description": "OpenAI GPT-4o-mini",
            "label": "New Model",
            "config": {
              "model": "mistralai/mistral-7b-instruct",
              "base_url": "https://openrouter.ai/api/v1",
              "api_key": os.getenv("OPENROUTER_API_KEY")
            }
          },
          "reflect_on_tool_use": false,
          "tool_call_summary_format": "simple"
        }
      }
    ],
    "tools": [
      {
        "provider": "autogen_agentchat.tools.WebSurferTool",
        "component_type": "tool",
        "version": 1,
        "component_version": 1,
        "label": "WebSurfer",
        "config": {
          "search_engine": "duckduckgo"
        }
      },
      {
        "provider": "autogen_agentchat.tools.SlackNotificationTool",
        "component_type": "tool",
        "version": 1,
        "component_version": 1,
        "label": "SlackNotifier",
        "config": {
          "webhook_url": "https://hooks.slack.com/services/your/webhook/url"
        }
      }
    ],
    "connections": [
      {
        "source": "Researcher",
        "target": "Summarizer",
        "data_mapping": {
          "text": "{{message}}"
        }
      },
      {
        "source": "Summarizer",
        "target": "Notifier",
        "data_mapping": {
          "summary": "{{message}}"
        }
      }
    ],
    "entry_point": "Researcher",
    "termination_condition": {
      "provider": "autogen_agentchat.base.OrTerminationCondition",
      "component_type": "termination",
      "version": 1,
      "component_version": 1,
      "label": "OrTerminationCondition",
      "config": {
        "conditions": [
          {
            "provider": "autogen_agentchat.conditions.TextMentionTermination",
            "component_type": "termination",
            "version": 1,
            "component_version": 1,
            "label": "TextMentionTermination",
            "config": {
              "text": "TERMINATE"
            }
          },
          {
            "provider": "autogen_agentchat.conditions.MaxMessageTermination",
            "component_type": "termination",
            "version": 1,
            "component_version": 1,
            "label": "MaxMessageTermination",
            "config": {
              "max_messages": 10,
              "include_agent_event": false
            }
          }
        ]
      }
    },
    "emit_team_events": false
  }
}