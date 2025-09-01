'use client'

import React, { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import ChatInterface from './chat/ChatInterface'
import { ScenarioType } from '@/types'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { LoginButton } from './auth/LoginButton'
import { ThemeToggle } from './ui/ThemeToggle'
import { 
  ShoppingCart, 
  Monitor, 
  Briefcase,
  Building2, 
  Sparkles, 
  TrendingUp,
  Users,
  Clock,
  MessageSquare,
  BarChart3,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

// Default built-in scenarios (will be replaced by dynamic loading)
const defaultScenarios = [
  {
    id: 'ECOMMERCE' as ScenarioType,
    name: 'E-Commerce Store',
    icon: ShoppingCart,
    color: 'from-green-500 to-emerald-600',
    description: 'Customer support for online retail business',
    features: [
      'Product recommendations',
      'Order tracking & status',
      'Returns & refunds',
      'Size guides & compatibility',
      'Payment assistance'
    ],
    demoQueries: [
      "What's your return policy?",
      "Track my order #12345",
      "Do you have this in size Medium?",
      "I need help with checkout"
    ],
    stats: {
      avgResponseTime: '1.2s',
      satisfaction: '94%',
      resolutionRate: '87%'
    }
  },
  {
    id: 'SAAS' as ScenarioType,
    name: 'SaaS Platform',
    icon: Monitor,
    color: 'from-blue-500 to-cyan-600',
    description: 'Technical support for software services',
    features: [
      'Account setup & configuration',
      'Feature explanations',
      'API documentation',
      'Billing & subscriptions',
      'Integration support'
    ],
    demoQueries: [
      "How do I set up my API key?",
      "What's included in the Pro plan?",
      "I'm having trouble with integration",
      "Can you explain this feature?"
    ],
    stats: {
      avgResponseTime: '1.8s',
      satisfaction: '91%',
      resolutionRate: '82%'
    }
  },
  {
    id: 'SERVICE_BUSINESS' as ScenarioType,
    name: 'Service Business',
    icon: Building2,
    color: 'from-purple-500 to-violet-600',
    description: 'Support for service-based businesses',
    features: [
      'Appointment scheduling',
      'Service area inquiries',
      'Pricing information',
      'Policy questions',
      'Emergency contact'
    ],
    demoQueries: [
      "Can I book for next Tuesday?",
      "What areas do you serve?",
      "How much does cleaning cost?",
      "Do you offer emergency services?"
    ],
    stats: {
      avgResponseTime: '1.5s',
      satisfaction: '96%',
      resolutionRate: '89%'
    }
  }
]

export const DemoPortal: React.FC = () => {
  const { data: session } = useSession()
  const [activeScenario, setActiveScenario] = useState<ScenarioType>('ECOMMERCE')
  const [currentConversation, setCurrentConversation] = useState<string | undefined>()
  const [scenarios, setScenarios] = useState(defaultScenarios)
  const [isLoadingScenarios, setIsLoadingScenarios] = useState(true)
  const [globalStats, setGlobalStats] = useState({
    totalConversations: 1247,
    activeUsers: 89,
    avgResponseTime: 1.5,
    satisfaction: 93.7
  })

  const activeScenarioConfig = scenarios.find(s => s.id === activeScenario) || scenarios[0]

  const handleConversationCreate = (conversation: any) => {
    setCurrentConversation(conversation.id)
    setGlobalStats(prev => ({
      ...prev,
      totalConversations: prev.totalConversations + 1
    }))
  }

  const handleMessageSend = (message: string) => {
    // Update stats on message send
  }

  const loadAllScenarios = async () => {
    try {
      setIsLoadingScenarios(true)
      
      // Load scenarios from API
      const response = await fetch('http://localhost:8000/api/v1/scenarios/')
      if (response.ok) {
        const apiScenarios = await response.json()
        
        // Convert API scenarios to component format
        const formattedScenarios = apiScenarios.map((scenario: any) => {
          // Map icon names to actual components
          const getIcon = (iconName: string) => {
            const iconMap: Record<string, any> = {
              'ShoppingCart': ShoppingCart,
              'Monitor': Monitor, 
              'Briefcase': Briefcase,
              'Settings': Briefcase, // Map unknown icons to Briefcase
              'ChefHat': Briefcase,
              'Heart': Briefcase,
              'Scale': Briefcase,
              'Building': Briefcase,
              'Zap': Briefcase
            }
            return iconMap[iconName] || Briefcase
          }

          return {
            id: scenario.id,
            name: scenario.name,
            icon: getIcon(scenario.icon || 'Briefcase'),
            color: scenario.color_gradient || 'from-gray-500 to-gray-600',
            description: scenario.description || 'Custom business scenario',
            features: [
              'Context-aware responses',
              'Business-specific knowledge',
              'Intelligent assistance',
              'Custom prompts'
            ],
            demoQueries: [
              'How can you help me?',
              'What services do you offer?',
              'Tell me about your business',
              'I need assistance'
            ],
            stats: {
              avgResponseTime: '1.2s',
              satisfaction: '95%', 
              resolutionRate: '90%'
            }
          }
        })
        
        // Combine with built-in scenarios that might not be in API yet
        const allScenarios = [...defaultScenarios]
        
        // Add custom scenarios
        formattedScenarios.forEach((customScenario: any) => {
          if (!allScenarios.find(s => s.id === customScenario.id)) {
            allScenarios.push(customScenario)
          }
        })
        
        setScenarios(allScenarios)
      }
    } catch (error) {
      console.error('Failed to load scenarios:', error)
      // Fallback to default scenarios
      setScenarios(defaultScenarios)
    } finally {
      setIsLoadingScenarios(false)
    }
  }

  // Load scenarios on component mount
  useEffect(() => {
    loadAllScenarios()
  }, [])

  return (
    <div className="min-h-screen enhanced-chat-container">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">BIWOCO AI Assistant</h1>
                <p className="text-muted-foreground">Multi-Scenario Customer Support Demo</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Global Stats */}
              <div className="hidden md:flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-blue-500" />
                  <span className="font-medium">{globalStats.totalConversations.toLocaleString()}</span>
                  <span className="text-muted-foreground">conversations</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-green-500" />
                  <span className="font-medium">{globalStats.activeUsers}</span>
                  <span className="text-muted-foreground">active</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-orange-500" />
                  <span className="font-medium">{globalStats.avgResponseTime}s</span>
                  <span className="text-muted-foreground">avg response</span>
                </div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-purple-500" />
                  <span className="font-medium">{globalStats.satisfaction}%</span>
                  <span className="text-muted-foreground">satisfaction</span>
                </div>
              </div>
              
              {/* Admin Link - Only show for admin users */}
              {session?.user?.role === 'admin' && (
                <a
                  href="/admin"
                  className="px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors border rounded-md hover:bg-accent"
                >
                  Admin
                </a>
              )}
              
              {/* Authentication */}
              <ThemeToggle />
              <LoginButton />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Scenario Selection Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold mb-4">Choose Scenario</h2>
                <div className="space-y-3">
                  {scenarios.map((scenario) => {
                    const Icon = scenario.icon
                    const isActive = activeScenario === scenario.id
                    
                    return (
                      <Card 
                        key={scenario.id} 
                        className={cn(
                          "cursor-pointer transition-all duration-200 hover:shadow-md",
                          isActive && "ring-2 ring-primary shadow-md"
                        )}
                        onClick={() => setActiveScenario(scenario.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center gap-3 mb-2">
                            <div className={cn(
                              "w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br",
                              scenario.color
                            )}>
                              <Icon className="w-4 h-4 text-white" />
                            </div>
                            <div className="font-medium">{scenario.name}</div>
                            {isActive && <Badge variant="default">Active</Badge>}
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {scenario.description}
                          </p>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {scenario.stats.avgResponseTime}
                            </div>
                            <div className="flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              {scenario.stats.satisfaction}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </div>

              {/* Features */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Key Features</CardTitle>
                  <CardDescription>{activeScenarioConfig.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    {activeScenarioConfig.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-2">
                        <Zap className="w-3 h-3 text-primary" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Quick Test Queries */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Try These</CardTitle>
                  <CardDescription>Sample questions to test</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {activeScenarioConfig.demoQueries.map((query, index) => (
                      <Button 
                        key={index}
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start text-left h-auto py-2 px-3"
                        onClick={() => {
                          // Auto-fill the chat input (would need to implement this)
                        }}
                      >
                        <MessageSquare className="w-3 h-3 mr-2 flex-shrink-0" />
                        <span className="text-xs">{query}</span>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Main Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="h-[500px] md:h-[600px] flex flex-col overflow-hidden">
              <CardHeader className="pb-0 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br",
                      activeScenarioConfig.color
                    )}>
                      <activeScenarioConfig.icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle>{activeScenarioConfig.name} Demo</CardTitle>
                      <CardDescription>{activeScenarioConfig.description}</CardDescription>
                    </div>
                  </div>
                  
                  {/* Performance Stats */}
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>{activeScenarioConfig.stats.resolutionRate} resolution</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-blue-500" />
                      <span>{activeScenarioConfig.stats.satisfaction} satisfaction</span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 p-0 overflow-hidden min-h-0">
                <ChatInterface
                  conversationId={currentConversation}
                  scenario={activeScenario}
                  onConversationCreate={handleConversationCreate}
                  onMessageSend={handleMessageSend}
                />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="p-6 text-center">
              <Sparkles className="w-10 h-10 mx-auto mb-4 text-primary" />
              <h3 className="font-semibold mb-2">AI-Powered Intelligence</h3>
              <p className="text-sm text-muted-foreground">
                Powered by Google Gemini 2.5 Flash with scenario-specific training
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <Zap className="w-10 h-10 mx-auto mb-4 text-primary" />
              <h3 className="font-semibold mb-2">Real-Time Responses</h3>
              <p className="text-sm text-muted-foreground">
                WebSocket-powered instant messaging with typing indicators
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <BarChart3 className="w-10 h-10 mx-auto mb-4 text-primary" />
              <h3 className="font-semibold mb-2">Advanced Analytics</h3>
              <p className="text-sm text-muted-foreground">
                Sentiment analysis, escalation detection, and performance metrics
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default DemoPortal