
import { useState } from 'react'
import './App.css'

const sampleMessages = [
  "My order ORD-1002 hasn't arrived. Can you check it?",
  'I received the wrong product instead of what I ordered.',
  "I don't recognize this payment on my account.",
  'What are your return policy and store opening hours?',
]

function App() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [activeView, setActiveView] = useState('support')

  const [orderId, setOrderId] = useState('')
  const [orderResult, setOrderResult] = useState(null)
  const [orderError, setOrderError] = useState('')
  const [isSearchingOrder, setIsSearchingOrder] = useState(false)

  async function handleOrderSearch(event) {
    event.preventDefault()

    const id = orderId.trim()
    if (!id || isSearchingOrder) return

    setIsSearchingOrder(true)
    setOrderResult(null)
    setOrderError('')

    try {
      const response = await fetch(
        `http://localhost:8000/orders/${encodeURIComponent(id)}`
      )

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Order not found. Check the order ID and try again.')
        }

        throw new Error('Could not retrieve the order. Please try again.')
      }

      const data = await response.json()
      setOrderResult(data)
    } catch (error) {
      setOrderError(
        error instanceof TypeError
          ? 'Could not connect to the backend. Make sure FastAPI is running.'
          : error.message
      )
    } finally {
      setIsSearchingOrder(false)
    }
  }

  async function handleAnalyze() {
    if (!message.trim() || isAnalyzing) return

    setIsAnalyzing(true)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/classify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.trim(),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'AI classification failed. Please try again.'
        )
      }

      setResult({
        message: message.trim(),
        status: 'AI analysis complete',
        intent: data.intent,
        urgency: data.urgency,
        humanReview: data.requires_human_review
          ? 'Required'
          : 'Not required',
      })
    } catch (error) {
      console.error('Classification error:', error)

      setResult({
        message: message.trim(),
        status: 'Analysis failed',
        error:
          error.message ||
          'Could not connect to the AI service. Check that the API is running.',
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <h2>ShopFlow AI</h2>
            <p>Support intelligence</p>
          </div>
        </div>

        <p className="nav-label">WORKSPACE</p>

        <button
          className={`nav-item ${activeView === 'support' ? 'active' : ''}`}
          onClick={() => setActiveView('support')}
        >
          ◈ <span>Support workspace</span>
        </button>

        <button
          className={`nav-item ${activeView === 'orders' ? 'active' : ''}`}
          onClick={() => setActiveView('orders')}
        >
          ▤ <span>Order lookup</span>
        </button>

        <div className="nav-item">⌁ <span>AI evaluations</span></div>

        <div className="sidebar-bottom">
          <span className="status-dot" />
          Local development
          <p>AI workflow demo</p>
        </div>
      </aside>

      <main className="main-content">
        <div key={activeView} className="view-transition">
          {activeView === 'orders' ? (
            <section className="panel order-lookup-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">ORDER INTELLIGENCE</p>
                  <h2>Order lookup</h2>
                </div>
                <span className="panel-symbol">▣</span>
              </div>

              <p className="muted">
                Enter an order ID to view its current status and delivery details.
              </p>

              <form
                className="order-search-form"
                onSubmit={handleOrderSearch}
              >
                <label htmlFor="order-id">ORDER ID</label>

                <div className="order-search-row">
                  <input
                    id="order-id"
                    type="text"
                    value={orderId}
                    onChange={(event) => {
                      setOrderId(event.target.value)
                      setOrderResult(null)
                      setOrderError('')
                    }}
                    placeholder="e.g. ORD-1001"
                    required
                  />

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={isSearchingOrder || !orderId.trim()}
                  >
                    {isSearchingOrder ? (
                      <>
                        <span className="loading-spinner" />
                        Searching...
                      </>
                    ) : (
                      <>
                        Search order <span>→</span>
                      </>
                    )}
                  </button>

                  <button
                    className="clear-button"
                    type="button"
                    onClick={() => {
                      setOrderId('')
                      setOrderResult(null)
                      setOrderError('')
                    }}
                    disabled={!orderId && !orderResult && !orderError}
                  >
                    Clear
                  </button>
                </div>
              </form>

              {orderError ? (
                <div className="order-empty-state order-error">
                  <div className="empty-icon">!</div>
                  <h3>Couldn't find that order</h3>
                  <p>{orderError}</p>
                </div>
              ) : orderResult ? (
                <div className="order-details">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">ORDER DETAILS</p>
                      <h3>{orderResult.order_id}</h3>
                    </div>

                    <span
                      className={`order-status-badge ${orderResult.order_status.toLowerCase()}`}
                    >
                      {orderResult.order_status}
                    </span>
                  </div>

                  <div className="order-detail-row">
                    <span>Product</span>
                    <strong>{orderResult.item_name}</strong>
                  </div>

                  <div className="order-detail-row">
                    <span>Customer email</span>
                    <strong>{orderResult.customer_email}</strong>
                  </div>

                  <div className="order-detail-row">
                    <span>Payment status</span>
                    <strong className="payment-status-badge">
                      {orderResult.payment_status}
                    </strong>
                  </div>

                  <div className="order-detail-row">
                    <span>Amount</span>
                    <strong>
                      {orderResult.currency}{' '}
                      {Number(orderResult.total_amount).toFixed(2)}
                    </strong>
                  </div>

                  <div className="order-detail-row">
                    <span>Order date</span>
                    <strong>{orderResult.order_date}</strong>
                  </div>

                  <div className="order-detail-row">
                    <span>Expected delivery</span>
                    <strong>
                      {orderResult.expected_delivery ?? 'Not available yet'}
                    </strong>
                  </div>
                </div>
              ) : (
                <div className="order-empty-state">
                  <div className="empty-icon">▣</div>
                  <h3>Ready to find an order</h3>
                  <p>
                    Search using an order ID to see its product, status,
                    payment, and delivery information.
                  </p>
                </div>
              )}
            </section>
          ) : (
            <>
              <header className="topbar">
                <div>
                  <p className="eyebrow">CUSTOMER OPERATIONS / WORKSPACE</p>
                  <h1>Support workspace</h1>
                </div>

                <div className="environment-tag">
                  <span className="status-dot" /> Local AI
                </div>
              </header>

              <section className="welcome">
                <div>
                  <p className="eyebrow">AI-POWERED CUSTOMER SUPPORT</p>
                  <h2>Resolve requests with clarity.</h2>
                  <p>
                    Classify customer messages, inspect orders, and identify
                    cases that need human attention.
                  </p>
                </div>

                <div className="welcome-icon">✳</div>
              </section>

              <section className="metrics">
                <article className="metric-card">
                  <span className="metric-icon">✉</span>
                  <p>Message analysis</p>
                  <h3>AI classification</h3>
                  <span className="metric-note">Intent · urgency · review</span>
                </article>

                <article className="metric-card">
                  <span className="metric-icon">▣</span>
                  <p>Order intelligence</p>
                  <h3>Order lookup</h3>
                  <span className="metric-note">Status · delivery · amount</span>
                </article>

                <article className="metric-card">
                  <span className="metric-icon">✓</span>
                  <p>Safety controls</p>
                  <h3>Human oversight</h3>
                  <span className="metric-note">Review flagged cases</span>
                </article>
              </section>

              <section className="workspace-grid">
                <article className="panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">STEP 01</p>
                      <h2>Analyze a customer message</h2>
                    </div>
                    <span className="panel-symbol">✳</span>
                  </div>

                  <p className="muted">
                    Enter a support request or start with one of the sample messages.
                  </p>

                  <label htmlFor="customer-message">CUSTOMER MESSAGE</label>
                  <textarea
                    id="customer-message"
                    value={message}
                    onChange={(event) => {
                      setMessage(event.target.value)
                      setResult(null)
                    }}
                    placeholder="e.g. My order is late and I'd like an update..."
                    rows={5}
                  />

                  <div className="input-actions">
                    <span className="sample-heading">TRY A SAMPLE</span>
                    <button
                      className="clear-button"
                      type="button"
                      onClick={() => {
                        setMessage('')
                        setResult(null)
                      }}
                      disabled={!message && !result}
                    >
                      Clear
                    </button>
                  </div>

                  <div className="sample-list">
                    {sampleMessages.map((sample) => (
                      <button
                        className="sample-button"
                        key={sample}
                        type="button"
                        onClick={() => {
                          setMessage(sample)
                          setResult(null)
                        }}
                      >
                        {sample} <span>↗</span>
                      </button>
                    ))}
                  </div>

                  <button
                    className="primary-button"
                    type="button"
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !message.trim()}
                  >
                    {isAnalyzing ? (
                      <>
                        <span className="loading-spinner" />
                        Analyzing message...
                      </>
                    ) : (
                      <>
                        Analyze message <span>→</span>
                      </>
                    )}
                  </button>

                  <p className="demo-note">
                    Powered by local Qwen AI · Results generated on request
                  </p>
                </article>

                <article className="panel result-panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">STEP 02</p>
                      <h2>Analysis results</h2>
                    </div>

                    <span
                      className={`result-status ${
                        !result
                          ? ''
                          : result.error
                            ? 'error'
                            : 'success'
                      }`}
                    >
                      {!result
                        ? 'READY'
                        : result.error
                          ? 'FAILED'
                          : 'AI COMPLETE'}
                    </span>
                  </div>

                  {!result ? (
                    <div className="empty-state">
                      <div className="empty-icon">⌁</div>
                      <h3>Your results will appear here</h3>
                      <p>
                        Submit a customer message to classify its intent,
                        urgency, and human-review requirement using the local AI.
                      </p>
                    </div>
                  ) : result.error ? (
                    <div className="empty-state">
                      <div className="empty-icon">!</div>
                      <h3>Analysis failed</h3>
                      <p>{result.error}</p>
                      <p className="muted">
                        Check that FastAPI and Ollama are running, then try again.
                      </p>
                    </div>
                  ) : (
                    <div className="result-content">
                      <div className="preview-banner">
                        AI classification returned successfully.
                      </div>

                      <p className="result-label">CUSTOMER MESSAGE</p>
                      <p className="result-message">{result.message}</p>

                      <div className="result-field">
                        <span>Intent</span>
                        <strong>{result.intent}</strong>
                      </div>

                      <div className="result-field">
                        <span>Urgency</span>
                        <strong>{result.urgency}</strong>
                      </div>

                      <div className="result-field">
                        <span>Human review</span>
                        <strong>{result.humanReview}</strong>
                      </div>

                      <p className="muted">
                        Classification is AI-generated. Human review is still
                        important for sensitive or uncertain customer cases.
                      </p>
                    </div>
                  )}
                </article>
              </section>

              <footer>
                <span>ShopFlow AI</span>
                <span>AI-assisted support · Human oversight matters</span>
              </footer>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
