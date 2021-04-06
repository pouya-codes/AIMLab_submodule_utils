
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

def merge_group(group1, group2):
    """Merge two deserialized JSON groups in Mitch format. When two groups have the same IDs, the patch paths in those groups are combined into one group.

    Parameters
    ----------
    group1 : {'chunks': [{'id': int, 'imgs': list of str}]}
        dict representing patch groups in Mitch format
    
    group2 : {'chunks': [{'id': int, 'imgs': list of str}]}
        dict representing patch groups in Mitch format

    Returns
    -------
    {'chunks': [{'id': int, 'imgs': list of str}]}
        Merged JSON groups.
    """
    outgroup = {'chunks': []}
    group1m = {chunks['id']: chunks['imgs'] for chunks in group1['chunks']}
    group2m = {chunks['id']: chunks['imgs'] for chunks in group2['chunks']}
    ids = set(group1m) | set(group2m)
    for id in ids:
        outgroup['chunks'].append({'id': id,
                'imgs': group1m.get(id, list()) + group2m.get(id, list())})
    return outgroup
