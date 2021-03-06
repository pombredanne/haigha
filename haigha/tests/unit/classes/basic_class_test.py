from chai import Chai

from haigha.classes import basic_class, ProtocolClass, BasicClass

class BasicClassTest(Chai):

  def setUp(self):
    super(BasicClassTest,self).setUp()
    ch = mock()
    ch.channel_id = 42
    self.klass = BasicClass( ch )

  def _BasicClass(self):
    # generator for instances
    ch = mock()
    ch.channel_id = 42
    return BasicClass( ch )

  def test_init(self):
    expect( ProtocolClass.__init__ ).args( 'args' )
    c = BasicClass( 'args' )

    assert_equals( 0, c._consumer_tag_id )
    assert_equals( [], c._pending_consumers )
    assert_equals( {}, c._consumer_cb )
    assert_equals( [], c._get_cb )
    assert_equals( [], c._recover_cb )
    assert_equals( [], c._cancel_cb )

  def test_generate_consumer_tag(self):
    assert_equals( 0, self.klass._consumer_tag_id )
    assert_equals( 'channel-42-1', self.klass._generate_consumer_tag() )
    assert_equals( 1, self.klass._consumer_tag_id )

  def test_qos_default_args(self):
    writer = mock()
    expect( mock( basic_class, 'Writer' ) ).returns( writer )
    expect( writer.write_long ).args( 0 )
    expect( writer.write_short ).args( 0 )
    expect( writer.write_bit ).args( False )
    expect( mock( basic_class, 'MethodFrame' ) ).args( 42, 60, 10, writer ).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )
    expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_qos_ok )

    self.klass.qos()

  def test_qos_with_args(self):
    writer = mock()
    expect( mock( basic_class, 'Writer' ) ).returns( writer )
    expect( writer.write_long ).args( 1 )
    expect( writer.write_short ).args( 2 )
    expect( writer.write_bit ).args( 3 )
    expect( mock( basic_class, 'MethodFrame' ) ).args( 42, 60, 10, writer ).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )
    expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_qos_ok )

    self.klass.qos(1, 2, 3)

  def test_recv_qos_ok(self):
    self.klass._recv_qos_ok( 'frame' )

  def test_consume_default_args(self):
    writer = mock()
    expect( self.klass._generate_consumer_tag ).returns( 'ctag' )
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_short ).args( self.klass.default_ticket )
    expect( writer.write_shortstr ).args( 'queue' )
    expect( writer.write_shortstr ).args( 'ctag' )
    expect( writer.write_bits ).args( False, True, False, True )
    expect( writer.write_table ).args( {} )
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 20, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )
    #expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_consume_ok )

    assert_equals( [], self.klass._pending_consumers )
    assert_equals( {}, self.klass._consumer_cb )
    self.klass.consume( 'queue', 'consumer' )
    assert_equals( [], self.klass._pending_consumers )
    assert_equals( {'ctag':'consumer'}, self.klass._consumer_cb )

  def test_consume_with_args_including_nowait_and_ticket(self):
    writer = mock()
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_short ).args( 'train' )
    expect( writer.write_shortstr ).args( 'queue' )
    expect( writer.write_shortstr ).args( 'stag' )
    expect( writer.write_bits ).args( 'nloc', 'nack', 'mine', False )
    expect( writer.write_table ).args( {} )
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 20, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )
    expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_consume_ok )

    assert_equals( [], self.klass._pending_consumers )
    assert_equals( {}, self.klass._consumer_cb )
    self.klass.consume( 'queue', 'consumer', consumer_tag='stag', no_local='nloc',
      no_ack='nack', exclusive='mine', nowait=False, ticket='train' )
    assert_equals( ['consumer'], self.klass._pending_consumers )
    assert_equals( {}, self.klass._consumer_cb )

  def test_consume_with_args_including_nowait_no_ticket(self):
    writer = mock()
    stub( self.klass._generate_consumer_tag )
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_short ).args( self.klass.default_ticket )
    expect( writer.write_shortstr ).args( 'queue' )
    expect( writer.write_shortstr ).args( 'stag' )
    expect( writer.write_bits ).args( 'nloc', 'nack', 'mine', False )
    expect( writer.write_table ).args( {} )
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 20, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )
    expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_consume_ok )

    assert_equals( [], self.klass._pending_consumers )
    assert_equals( {}, self.klass._consumer_cb )
    self.klass.consume( 'queue', 'consumer', consumer_tag='stag', no_local='nloc',
      no_ack='nack', exclusive='mine', nowait=False )
    assert_equals( ['consumer'], self.klass._pending_consumers )
    assert_equals( {}, self.klass._consumer_cb )

  def test_recv_consume_ok(self):
    frame = mock()
    expect( frame.args.read_shortstr ).returns( 'ctag' )
    self.klass._pending_consumers = ['consumer']
    
    assert_equals( {}, self.klass._consumer_cb )
    self.klass._recv_consume_ok( frame )
    assert_equals( {'ctag':'consumer'}, self.klass._consumer_cb )
    assert_equals( [], self.klass._pending_consumers )

  def test_cancel_default_args(self):
    writer = mock()
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_shortstr ).args( '' )
    expect( writer.write_bit ).args( True )
    
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 30, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )
    
    self.klass._consumer_cb[ '' ] = 'foo'
    assert_equals( [], self.klass._cancel_cb )
    self.klass.cancel()
    assert_equals( [], self.klass._cancel_cb )
    assert_equals( {}, self.klass._consumer_cb )

  def test_cancel_nowait_and_consumer_tag_not_registered(self):
    writer = mock()
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_shortstr ).args( 'ctag' )
    expect( writer.write_bit ).args( True )
    
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 30, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )

    expect( self.klass.logger.warning ).args( 
      'no callback registered for consumer tag " %s "', 'ctag' )
    
    assert_equals( [], self.klass._cancel_cb )
    self.klass.cancel( consumer_tag='ctag' )
    assert_equals( [], self.klass._cancel_cb )
    assert_equals( {}, self.klass._consumer_cb )

  def test_cancel_wait(self):
    writer = mock()
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_shortstr ).args( '' )
    expect( writer.write_bit ).args( False )
    
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 30, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )

    expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_cancel_ok )
    
    assert_equals( [], self.klass._cancel_cb )
    self.klass.cancel( nowait=False )
    assert_equals( [None], self.klass._cancel_cb )
    assert_equals( {}, self.klass._consumer_cb )

  def test_cancel_wait_with_user_cb(self):
    writer = mock()
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_shortstr ).args( '' )
    expect( writer.write_bit ).args( False )
    
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 30, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )

    expect( self.klass.channel.add_synchronous_cb ).args( self.klass._recv_cancel_ok )
    
    assert_equals( [], self.klass._cancel_cb )
    self.klass.cancel( nowait=False, cb='user_cb' )
    assert_equals( ['user_cb'], self.klass._cancel_cb )
    assert_equals( {}, self.klass._consumer_cb )

  def test_cancel_resolves_to_ctag_when_consumer_arg_supplied(self):
    writer = mock()
    expect( mock(basic_class, 'Writer') ).returns( writer )
    expect( writer.write_shortstr ).args( 'ctag' )
    expect( writer.write_bit ).args( True )
    
    expect( mock(basic_class,'MethodFrame') ).args(42, 60, 30, writer).returns( 'frame' )
    expect( self.klass.send_frame ).args( 'frame' )

    self.klass._consumer_cb[ 'ctag' ] = 'consumer'
    assert_equals( [], self.klass._cancel_cb )
    self.klass.cancel( consumer='consumer' )
    assert_equals( [], self.klass._cancel_cb )
    assert_equals( {}, self.klass._consumer_cb )

  def test_recv_cancel_ok_when_consumer_and_callback(self):
    frame = mock()
    cancel_cb = mock()
    expect( frame.args.read_shortstr ).returns( 'ctag' )
    self.klass._consumer_cb['ctag'] = 'foo'
    self.klass._cancel_cb = [ cancel_cb ]
    expect( cancel_cb )

    self.klass._recv_cancel_ok( frame )

  def test_recv_cancel_ok_when_no_consumer_or_callback(self):
    frame = mock()
    expect( frame.args.read_shortstr ).returns( 'ctag' )
    expect( self.klass.logger.warning ).args( 
      'no callback registered for consumer tag " %s "', 'ctag' )
    self.klass._cancel_cb = [ None ]

    self.klass._recv_cancel_ok( frame )
