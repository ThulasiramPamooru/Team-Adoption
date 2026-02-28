import { useEffect, useRef } from "react";
import { useWorkflowStore } from "@/store/workflowStore";
import type { WsMessage } from "@/types";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export function useWorkflowWebSocket(workflowId: string | null, token: string | null) {
  const ws = useRef<WebSocket | null>(null);
  const { updateWorkflowFromWs, setWsConnected } = useWorkflowStore();
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!workflowId || !token) return;

    const connect = () => {
      ws.current = new WebSocket(
        `${WS_URL}/ws/workflow/${workflowId}?token=${token}`
      );

      ws.current.onopen = () => {
        setWsConnected(true);
      };

      ws.current.onmessage = (event) => {
        try {
          const msg: WsMessage = JSON.parse(event.data);
          updateWorkflowFromWs(msg);
        } catch {
          // ignore malformed messages
        }
      };

      ws.current.onclose = () => {
        setWsConnected(false);
        // Reconnect after 3 seconds
        reconnectTimer.current = setTimeout(connect, 3000);
      };

      ws.current.onerror = () => {
        ws.current?.close();
      };
    };

    connect();

    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      ws.current?.close();
      setWsConnected(false);
    };
  }, [workflowId, token, updateWorkflowFromWs, setWsConnected]);

  return { connected: useWorkflowStore((s) => s.wsConnected) };
}
