
import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

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

  const [reviewCases, setReviewCases] = useState([])
  const [reviewError, setReviewError] = useState('')
  const [isLoadingReviews, setIsLoadingReviews] = useState(false)
  const [completingReviewId, setCompletingReviewId] = useState(null)
  const [reviewFilter, setReviewFilter] = useState('pending')

  async function handleOrderSearch(event) {
    event.preventDefault()

    const id = orderId.trim()
    if (!id || isSearchingOrder) return

    setIsSearchingOrder(true)
    setOrderResult(null)
    setOrderError('')

    try {
      const response = await fetch(
        `${API_URL}/orders/${encodeURIComponent(id)}`
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Could not retrieve the order. Please try again.'
        )
      }

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
      const response = await fetch(`${API_URL}/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message.trim() }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'AI classification failed. Please try again.'
        )
      }

      setResult({
        message: message.trim(),
        intent: data.intent,
        urgency: data.urgency,
        humanReview: data.requires_human_review
          ? 'Required'
          : 'Not required',
      })

      // Refresh the queue if the backend saved a human-review case.
      if (data.requires_human_review) {
        loadReviewCases()
      }
    } catch (error) {
      console.error('Classification error:', error)

      setResult({
        message: message.trim(),
        error:
          error.message ||
          'Could not connect to the AI service. Check that the API is running.',
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function loadReviewCases() {
    setIsLoadingReviews(true)
    setReviewError('')

    try {
      const response = await fetch(`${API_URL}/review-cases`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Could not load review cases.')
      }

      setReviewCases(data)
    } catch (error) {
      setReviewError(
        error instanceof TypeError
          ? 'Could not connect to the backend. Make sure FastAPI is running.'
          : error.message
      )
    } finally {
      setIsLoadingReviews(false)
    }
  }

  async function handleCompleteReview(reviewId) {
    if (completingReviewId !== null) return

    setCompletingReviewId(reviewId)
    setReviewError('')

    try {
      const response = await fetch(
        `${API_URL}/review-cases/${reviewId}/complete`,
        { method: 'POST' }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Could not complete this review.')
      }

      // Update the case locally using the server's response.
      setReviewCases((currentCases) =>
        currentCases.map((reviewCase) =>
          reviewCase.review_id === reviewId ? data : reviewCase
        )
      )
    } catch (error) {
      setReviewError(
        error instanceof TypeError
          ? 'Could not connect to the backend. Make sure FastAPI is running.'
          : error.message
      )
    } finally {
      setCompletingReviewId(null)
    }
  }

  function openReviews() {
    setActiveView('reviews')
    loadReviewCases()
  }

  const pendingCount = reviewCases.filter(
    (reviewCase) => reviewCase.review_status === 'pending'
  ).length

  const filteredReviewCases = reviewCases.filter((reviewCase) =>
    reviewFilter === 'all'
      ? true
      : reviewCase.review_status === reviewFilter
  )

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

        <button
          className={`nav-item ${activeView === 'reviews' ? 'active' : ''}`}
          onClick={openReviews}
        >
          ⌁ <span>Human review</span>
          {pendingCount > 0 && (
            <span className="review-nav-count">{pendingCount}</span>
          )}
        </button>

        <div className="sidebar-bottom">
          <span className="status-dot" />
          Local development
          <p>AI workflow demo</p>
        </div>
      </aside>

      <main className="main-content">
        <div key={activeView} className="view-transition">

          {/* ORDER LOOKUP */}
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

              <form className="order-search-form" onSubmit={handleOrderSearch}>
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
                    {isSearchingOrder ? 'Searching...' : 'Search order →'}
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

          ) : activeView === 'reviews' ? (

            /* HUMAN REVIEW QUEUE */
            <>
              <header className="topbar">
                <div>
                  <p className="eyebrow">CUSTOMER OPERATIONS / OVERSIGHT</p>
                  <h1>Human review queue</h1>
                </div>
                <div className="environment-tag">
                  <span className="status-dot" /> Review management
                </div>
              </header>

              <section className="welcome">
                <div>
                  <p className="eyebrow">HUMAN-IN-THE-LOOP WORKFLOW</p>
                  <h2>Keep people in the loop.</h2>
                  <p>
                    Review customer messages flagged by the AI before
                    considering them handled.
                  </p>
                </div>
                <div className="welcome-icon">✓</div>
              </section>

              <section className="metrics">
                <article className="metric-card">
                  <span className="metric-icon">⌁</span>
                  <p>Pending reviews</p>
                  <h3>{pendingCount}</h3>
                  <span className="metric-note">Awaiting human attention</span>
                </article>

                <article className="metric-card">
                  <span className="metric-icon">✓</span>
                  <p>Reviewed cases</p>
                  <h3>
                    {reviewCases.filter(
                      (item) => item.review_status === 'reviewed'
                    ).length}
                  </h3>
                  <span className="metric-note">Completed reviews</span>
                </article>

                <article className="metric-card">
                  <span className="metric-icon">▤</span>
                  <p>Total cases</p>
                  <h3>{reviewCases.length}</h3>
                  <span className="metric-note">Loaded from the database</span>
                </article>
              </section>

              <section className="panel review-queue-panel">
                <div className="panel-heading review-queue-heading">
                  <div>
                    <p className="eyebrow">CASE MANAGEMENT</p>
                    <h2>Customer cases</h2>
                  </div>

                  <button
                    className="clear-button"
                    type="button"
                    onClick={loadReviewCases}
                    disabled={isLoadingReviews}
                  >
                    {isLoadingReviews ? 'Refreshing...' : '↻ Refresh'}
                  </button>
                </div>

                <div className="review-filters">
                  <button
                    type="button"
                    className={`review-filter ${reviewFilter === 'pending' ? 'active' : ''}`}
                    onClick={() => setReviewFilter('pending')}
                  >
                    Pending
                  </button>
                  <button
                    type="button"
                    className={`review-filter ${reviewFilter === 'reviewed' ? 'active' : ''}`}
                    onClick={() => setReviewFilter('reviewed')}
                  >
                    Reviewed
                  </button>
                  <button
                    type="button"
                    className={`review-filter ${reviewFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setReviewFilter('all')}
                  >
                    All cases
                  </button>
                </div>

                {reviewError && (
                  <div className="review-error" role="alert">
                    <strong>Something went wrong</strong>
                    <p>{reviewError}</p>
                    <button
                      className="clear-button"
                      type="button"
                      onClick={loadReviewCases}
                    >
                      Try again
                    </button>
                  </div>
                )}

                {isLoadingReviews && reviewCases.length === 0 ? (
                  <div className="review-empty-state">
                    <span className="loading-spinner" />
                    <p>Loading review cases...</p>
                  </div>
                ) : filteredReviewCases.length === 0 ? (
                  <div className="review-empty-state">
                    <div className="empty-icon">
                      {reviewFilter === 'pending' ? '✓' : '⌁'}
                    </div>
                    <h3>
                      {reviewFilter === 'pending'
                        ? 'No pending reviews'
                        : 'No cases found'}
                    </h3>
                    <p>
                      {reviewFilter === 'pending'
                        ? 'New cases requiring human attention will appear here.'
                        : 'Try another filter or refresh the queue.'}
                    </p>
                  </div>
                ) : (
                  <div className="review-case-list">
                    {filteredReviewCases.map((reviewCase) => (
                      <article
                        className="review-case"
                        key={reviewCase.review_id}
                      >
                        <div className="review-case-top">
                          <div>
                            <p className="eyebrow">
                              REVIEW #{reviewCase.review_id}
                            </p>
                            <span
                              className={`review-status ${reviewCase.review_status}`}
                            >
                              {reviewCase.review_status === 'pending'
                                ? 'Pending review'
                                : 'Reviewed'}
                            </span>
                          </div>

                          <span
                            className={`urgency-badge ${reviewCase.urgency.toLowerCase()}`}
                          >
                            {reviewCase.urgency} urgency
                          </span>
                        </div>

                        <p className="review-customer-message">
                          {reviewCase.customer_message}
                        </p>

                        <div className="review-case-details">
                          <div>
                            <span>Predicted intent</span>
                            <strong>{reviewCase.intent.replaceAll('_', ' ')}</strong>
                          </div>
                          <div>
                            <span>Created</span>
                            <strong>{reviewCase.created_at}</strong>
                          </div>
                        </div>

                        <div className="review-case-actions">
                          {reviewCase.review_status === 'pending' ? (
                            <button
                              className="primary-button"
                              type="button"
                              onClick={() =>
                                handleCompleteReview(reviewCase.review_id)
                              }
                              disabled={completingReviewId !== null}
                            >
                              {completingReviewId === reviewCase.review_id
                                ? 'Completing review...'
                                : '✓ Mark as reviewed'}
                            </button>
                          ) : (
                            <p className="review-completed-note">
                              ✓ Reviewed
                              {reviewCase.reviewed_at
                                ? ` on ${reviewCase.reviewed_at}`
                                : ''}
                            </p>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <footer>
                <span>ShopFlow AI</span>
                <span>AI-assisted support · Human oversight matters</span>
              </footer>
            </>

          ) : (

            /* SUPPORT WORKSPACE */
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
                      <>Analyze message <span>→</span></>
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
                        !result ? '' : result.error ? 'error' : 'success'
                      }`}
                    >
                      {!result ? 'READY' : result.error ? 'FAILED' : 'AI COMPLETE'}
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

                      {result.humanReview === 'Required' && (
                        <button
                          className="clear-button"
                          type="button"
                          onClick={openReviews}
                        >
                          Open human review queue →
                        </button>
                      )}

                      <p className="muted">
                        Classification is AI-generated. Human review remains
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
