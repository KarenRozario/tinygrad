import torch
import numpy as np
from tinygrad.llops.ops_cpu import CPUBuffer
from tinygrad.ops import MovementOps, ProcessingOps

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
class TorchBuffer(torch.Tensor):
  def __new__(cls, shape):
    if isinstance(shape, torch.Tensor):
      return super().__new__(cls, shape)
    else:
      return TorchBuffer(torch.zeros(shape)).to(device)
  custompad = lambda x,padding: torch.nn.functional.pad(x, [item for sublist in padding[::-1] for item in sublist])
  @staticmethod
  def fromCPU(data):
    return TorchBuffer(torch.from_numpy(data).requires_grad_(False)).to(device)
  def toCPU(x):
    return x.cpu().numpy()
  def getdtype(self):
    return np.float32

  unary_op, binary_op, reduce_op, movement_op = CPUBuffer.unary_op, CPUBuffer.binary_op, CPUBuffer.reduce_op, CPUBuffer.movement_op

  def processing_op(x,op,w,C):
    assert op == ProcessingOps.CONV, f"{op} isn't supported"
    x = x.movement_op(MovementOps.SLICE, ((0, x.shape[0]), (0, x.shape[1]), (-C.py, x.shape[2]+C.py_), (-C.px, x.shape[3]+C.px_)))
    return torch.conv2d(x, w, stride=(C.sy, C.sx), groups=C.groups, dilation=(C.dy, C.dx))
