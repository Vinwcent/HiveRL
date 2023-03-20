
def get_greedy_action_index(state, action_space, net):
    '''
    state: Tensor
    action_space: Tensor

    Compute the greedy action index in action space that net in state would take
    '''
    state = state.repeat(action_space.shape[0], 1, 1, 1)
    with torch.no_grad():
        values = net(state, action_space)
    index = torch.argmax(values)
    return index

def select_action_index(state, action_space, net):
    '''
    state: Tensor
    action_space: Tensor

    Compute the index of the next action
    '''
    if random.random() < EPS:
        exploration_index = random.randint(0, action_space.shape[0]-1)
        print("Exploration action")
        return exploration_index
    else:
        exploitation_index = get_greedy_action_index(state, action_space, net)
        return exploitation_index

def select_action(state, env):
    '''
    Select the next action to play
    '''
    action_space_numpy = env.get_current_action_space()

    action_space_torch = torch.Tensor(action_space_numpy)
    action_space_torch = action_space_torch.to(device)
    index = select_action_index(state, action_space_torch, policy_net)

    return action_space_numpy[index], action_space_torch[index]
