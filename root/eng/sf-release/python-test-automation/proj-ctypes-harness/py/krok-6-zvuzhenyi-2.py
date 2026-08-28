from collections import deque
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize, invariant, precondition
from ringbuf_ffi import RingBuffer


class RingBufferMatchesDeque(RuleBasedStateMachine):
    rb = None

    @initialize(cap=st.integers(min_value=1, max_value=8))
    def make(self, cap):
        self.cap   = cap
        self.rb    = RingBuffer(cap)
        self.model = deque(maxlen=cap)

    @rule(v=st.integers(min_value=0, max_value=255))
    def push(self, v):
        was_full  = len(self.model) == self.cap
        displaced = self.rb.push(v)
        self.model.append(v)
        assert displaced == was_full, f"push: C каже {displaced}, модель — {was_full}"

    @rule()
    def pop(self):
        got  = self.rb.pop()
        want = self.model.popleft() if self.model else None
        assert got == want, f"pop: C дало {got}, модель — {want}"

    @precondition(lambda self: self.rb is not None)
    @invariant()
    def length_matches(self):
        assert len(self.rb) == len(self.model)

    def teardown(self):
        if self.rb:
            self.rb.close()


TestRingBuffer = RingBufferMatchesDeque.TestCase
