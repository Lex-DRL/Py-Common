__author__ = 'DRL'

nk_script = r'e:\1-Projects\_AAA\FlameThrower\_Compose.nk'.replace('\\', '/')
write_node_name = 'Write1'
start_frame = 1
end_frame = 125
increment_frame = 1

import nuke as nk
from drl_common import filesystem as fs

nk.scriptOpen(nk_script)
w = nk.toNode(write_node_name)
nk.execute(w, start_frame, end_frame, increment_frame, continueOnError=False)