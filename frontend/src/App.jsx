import { useEffect, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function App() {
  const [menu, setMenu] = useState([]);
  const [qty, setQty] = useState({});
  const [message, setMessage] = useState("");
  const [orderId, setOrderId] = useState("");
  const [orderInfo, setOrderInfo] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/menu`)
      .then((r) => r.json())
      .then(setMenu)
      .catch(() => setError("Menu load aagala. Backend run aagudhaanu paarunga."));
  }, []);

  const placeOrder = async (item) => {
    const quantity = Number(qty[item.id] || 1);
    try {
      const r = await fetch(`${API}/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: item.id, quantity }),
      });
      const data = await r.json();
      setMessage(`Order #${data.order_id} placed: ${quantity} x ${item.name}`);
      setOrderId(String(data.order_id));
    } catch {
      setMessage("Order fail aachu.");
    }
  };

  const checkOrder = async () => {
    setOrderInfo(null);
    const r = await fetch(`${API}/orders/${orderId}`);
    setOrderInfo(r.ok ? await r.json() : { error: "Order kidaikala" });
  };

  return (
    <div className="container">
      <h1>OrderPulse</h1>
      <p className="sub">Food ordering app</p>

      {error && <p className="error">{error}</p>}

      <h2>Menu</h2>
      <div className="menu">
        {menu.map((item) => (
          <div className="card" key={item.id}>
            <h3>{item.name}</h3>
            <p>₹{item.price}</p>
            <input
              type="number"
              min="1"
              defaultValue="1"
              onChange={(e) => setQty({ ...qty, [item.id]: e.target.value })}
            />
            <button onClick={() => placeOrder(item)}>Order</button>
          </div>
        ))}
      </div>

      {message && <p className="success">{message}</p>}

      <h2>Order status</h2>
      <div className="status">
        <input
          placeholder="Order ID"
          value={orderId}
          onChange={(e) => setOrderId(e.target.value)}
        />
        <button onClick={checkOrder}>Check</button>
      </div>
      {orderInfo && <pre>{JSON.stringify(orderInfo, null, 2)}</pre>}
    </div>
  );
}