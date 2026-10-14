import React, { createContext, useContext, useState } from 'react';
import PacketInspectorModal from '../components/common/PacketInspectorModal';

const PacketModalContext = createContext({
  inspectPacket: () => {},
  closeModal: () => {},
  selectedPacket: null
});

export const PacketModalProvider = ({ children }) => {
  const [selectedPacket, setSelectedPacket] = useState(null);

  const inspectPacket = (packet) => {
    if (!packet) return;
    setSelectedPacket(packet);
  };

  const closeModal = () => {
    setSelectedPacket(null);
  };

  return (
    <PacketModalContext.Provider value={{ inspectPacket, closeModal, selectedPacket }}>
      {children}
      {selectedPacket && (
        <PacketInspectorModal packet={selectedPacket} onClose={closeModal} />
      )}
    </PacketModalContext.Provider>
  );
};

export const usePacketModal = () => useContext(PacketModalContext);
