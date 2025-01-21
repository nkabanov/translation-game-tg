global user_states
user_states={}

def set_user_state(chat_id, state):
    user_states[chat_id] = state

def get_user_state(chat_id):
    return user_states.get(chat_id)

def clear_user_state(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]