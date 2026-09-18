def build_system_prompt(memory):
    system_prompt = "You are FRIDAY, a sharp and loyal AI assistant. Keep answers short and direct."
    if memory.get("name"):
        system_prompt += f" The user's name is {memory['name']}. Call them by their name sometimes."
    if memory.get("facts"):
        system_prompt += f" Facts about the user:\n{format_facts(memory['facts'])}"

    return system_prompt
def trim(messages, keep=10):
    if len(messages) <= keep:
        return messages

    trimmed = [messages[0]] + messages[-(keep - 1):]
    return trimmed
def format_facts(facts):
    lines = []
    for category, value in facts.items():
        if isinstance(value, dict):
            for k, v in value.items():
                lines.append(f"- {category}.{k}: {v}")
        else:
            lines.append(f"- {category}: {value}")
    return "\n".join(lines)
