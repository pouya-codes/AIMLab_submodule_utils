
def convert_yiping_to_mitch_format(groups):
    '''Convert a deserialized JSON representing patch groups in Yiping format into Mitch format

    Parameters
    ----------
    groups : {'group_(int)': list of str}
        dict representing patch groups in Yiping format
    
    Returns
    -------
    {'chunks': [{'id': int, 'imgs': list of str}]}
        dict representing patch groups in Mitch format
    '''
    mitch_groups = {'chunks': []}
    groups_items = list(groups.items())
    groups_items.sort(key=lambda item: int(item[0].split('_')[-1]))
    for index, (_, patches) in enumerate(groups_items):
        mitch_groups['chunks'].append({'id': index, 'imgs': patches})
    return mitch_groups

def convert_mitch_to_yiping_format(groups):
    '''Convert a deserialized JSON representing patch groups in Mitch format into Yiping format

    Parameters
    ----------
    groups : {'chunks': [{'id': int, 'imgs': list of str}]}
        dict representing patch groups in Mitch format
    
    Returns
    -------
    {'group_(int)': list of str}
        dict representing patch groups in Yiping format
    '''
    yiping_groups = {}
    for index, chunk in enumerate(groups['chunks']):
        yiping_groups['group_' + str(index + 1)] = chunk['imgs']
    return yiping_groups
