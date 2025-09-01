'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Plus, 
  Sparkles, 
  Palette,
  MessageSquare,
  Settings,
  ChefHat,
  Heart,
  Scale,
  Building,
  Zap,
  CheckCircle,
  XCircle
} from 'lucide-react'

interface ScenarioTemplate {
  id: string
  name: string
  description: string
  icon: string
  color_gradient: string
  system_prompt: string
  sample_queries: string[]
  specialization: string[]
}

interface CustomScenario {
  id: string
  name: string
  description: string
  icon: string
  color_gradient: string
  system_prompt: string
  sample_queries: string[]
  type: 'built_in' | 'custom'
}

const iconOptions = [
  { value: 'ChefHat', label: 'Restaurant', icon: ChefHat },
  { value: 'Heart', label: 'Healthcare', icon: Heart },
  { value: 'Scale', label: 'Legal', icon: Scale },
  { value: 'Building', label: 'Real Estate', icon: Building },
  { value: 'Zap', label: 'Energy', icon: Zap },
  { value: 'Settings', label: 'Technical', icon: Settings }
]

const colorOptions = [
  { value: 'from-red-500 to-pink-600', label: 'Red to Pink' },
  { value: 'from-orange-500 to-red-600', label: 'Orange to Red' }, 
  { value: 'from-amber-500 to-orange-600', label: 'Amber to Orange' },
  { value: 'from-green-500 to-emerald-600', label: 'Green to Emerald' },
  { value: 'from-blue-500 to-cyan-600', label: 'Blue to Cyan' },
  { value: 'from-indigo-500 to-purple-600', label: 'Indigo to Purple' },
  { value: 'from-purple-500 to-pink-600', label: 'Purple to Pink' },
  { value: 'from-gray-500 to-slate-600', label: 'Gray to Slate' }
]

export default function ScenarioCreator() {
  const [templates, setTemplates] = useState<ScenarioTemplate[]>([])
  const [scenarios, setScenarios] = useState<CustomScenario[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    description: '',
    icon: 'Settings',
    color_gradient: 'from-blue-500 to-cyan-600',
    system_prompt: '',
    sample_queries: ['']
  })
  const [message, setMessage] = useState<string | null>(null)

  const loadTemplates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/scenarios/templates')
      if (response.ok) {
        const data = await response.json()
        setTemplates(data)
      }
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const loadScenarios = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/scenarios/')
      if (response.ok) {
        const data = await response.json()
        setScenarios(data)
      }
    } catch (error) {
      console.error('Failed to load scenarios:', error)
    }
  }

  const createFromTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/scenarios/from-template/${templateId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        setMessage(`✅ Created ${templateId} scenario successfully!`)
        await loadScenarios()
      } else {
        const error = await response.json()
        setMessage(`❌ Error: ${error.detail}`)
      }
    } catch (error) {
      setMessage(`❌ Failed to create scenario: ${error}`)
    }
  }

  const createCustomScenario = async () => {
    if (!formData.id || !formData.name || !formData.system_prompt) {
      setMessage('❌ Please fill in all required fields')
      return
    }

    setIsCreating(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/scenarios/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          sample_queries: formData.sample_queries.filter(q => q.trim())
        })
      })

      if (response.ok) {
        setMessage(`✅ Created custom scenario "${formData.name}" successfully!`)
        setShowForm(false)
        setFormData({
          id: '', name: '', description: '', icon: 'Settings',
          color_gradient: 'from-blue-500 to-cyan-600', system_prompt: '', sample_queries: ['']
        })
        await loadScenarios()
      } else {
        const error = await response.json()
        setMessage(`❌ Error: ${error.detail}`)
      }
    } catch (error) {
      setMessage(`❌ Failed to create scenario: ${error}`)
    } finally {
      setIsCreating(false)
    }
  }

  const deleteScenario = async (scenarioId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/scenarios/${scenarioId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setMessage(`✅ Deleted scenario successfully`)
        await loadScenarios()
      }
    } catch (error) {
      setMessage(`❌ Failed to delete scenario: ${error}`)
    }
  }

  const addSampleQuery = () => {
    setFormData(prev => ({
      ...prev,
      sample_queries: [...prev.sample_queries, '']
    }))
  }

  const removeSampleQuery = (index: number) => {
    setFormData(prev => ({
      ...prev,
      sample_queries: prev.sample_queries.filter((_, i) => i !== index)
    }))
  }

  const updateSampleQuery = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      sample_queries: prev.sample_queries.map((q, i) => i === index ? value : q)
    }))
  }

  useEffect(() => {
    loadTemplates()
    loadScenarios()
  }, [])

  const SelectedIcon = iconOptions.find(opt => opt.value === formData.icon)?.icon || Settings

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Scenario Management</h2>
          <p className="text-muted-foreground">
            Create custom business scenarios or use pre-built templates.
          </p>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Custom Scenario
        </Button>
      </div>

      {message && (
        <Alert className={`border-0 shadow-md ${
          message.includes('✅') 
            ? 'bg-green-50 dark:bg-green-950 text-green-800 dark:text-green-200'
            : 'bg-red-50 dark:bg-red-950 text-red-800 dark:text-red-200'
        }`}>
          <div className="flex items-center gap-2">
            {message.includes('✅') ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600" />
            )}
            <AlertDescription>{message}</AlertDescription>
          </div>
        </Alert>
      )}

      {/* Quick Setup Templates */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle>Quick Setup Templates</CardTitle>
              <CardDescription>
                Start with pre-configured scenarios for common business types.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {templates.map((template) => {
              const IconComponent = iconOptions.find(opt => opt.value === template.icon)?.icon || Settings
              return (
                <Card key={template.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${template.color_gradient} flex items-center justify-center`}>
                        <IconComponent className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{template.name}</h4>
                        <p className="text-xs text-muted-foreground">{template.description}</p>
                      </div>
                    </div>
                    <Button 
                      onClick={() => createFromTemplate(template.id)}
                      variant="outline" 
                      className="w-full"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Template
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Custom Creation Form */}
      {showForm && (
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle>Create Custom Scenario</CardTitle>
            <CardDescription>
              Build a completely custom business scenario with your own prompts and configuration.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Scenario ID *</Label>
                <Input
                  placeholder="e.g., RESTAURANT, HEALTHCARE"
                  value={formData.id}
                  onChange={(e) => setFormData(prev => ({ ...prev, id: e.target.value.toUpperCase() }))}
                />
              </div>
              <div className="space-y-2">
                <Label>Display Name *</Label>
                <Input
                  placeholder="e.g., Restaurant Business"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Description</Label>
              <Input
                placeholder="Brief description of this business type"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Icon</Label>
                <Select value={formData.icon} onValueChange={(value) => setFormData(prev => ({ ...prev, icon: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {iconOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        <div className="flex items-center gap-2">
                          <option.icon className="w-4 h-4" />
                          {option.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Color Theme</Label>
                <Select value={formData.color_gradient} onValueChange={(value) => setFormData(prev => ({ ...prev, color_gradient: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {colorOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Preview */}
            <div className="space-y-2">
              <Label>Preview</Label>
              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${formData.color_gradient} flex items-center justify-center`}>
                    <SelectedIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium">{formData.name || 'Custom Scenario'}</h4>
                    <p className="text-sm text-muted-foreground">{formData.description || 'Custom business scenario'}</p>
                  </div>
                </div>
              </Card>
            </div>

            <div className="space-y-2">
              <Label>AI System Prompt *</Label>
              <Textarea
                placeholder="You are a helpful assistant for a [business type]. Focus on..."
                value={formData.system_prompt}
                onChange={(e) => setFormData(prev => ({ ...prev, system_prompt: e.target.value }))}
                rows={6}
              />
            </div>

            <div className="space-y-2">
              <Label>Sample Questions</Label>
              {formData.sample_queries.map((query, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    placeholder={`Sample question ${index + 1}`}
                    value={query}
                    onChange={(e) => updateSampleQuery(index, e.target.value)}
                  />
                  {formData.sample_queries.length > 1 && (
                    <Button
                      variant="outline"
                      onClick={() => removeSampleQuery(index)}
                      size="icon"
                    >
                      <XCircle className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
              <Button variant="outline" onClick={addSampleQuery} className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add Sample Question
              </Button>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={createCustomScenario}
                disabled={isCreating}
                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              >
                {isCreating ? (
                  <>
                    <Settings className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Create Scenario
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Existing Scenarios */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle>Active Scenarios</CardTitle>
              <CardDescription>
                Manage all available business scenarios for your AI assistant.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scenarios.map((scenario) => {
              const IconComponent = iconOptions.find(opt => opt.value === scenario.icon)?.icon || Settings
              return (
                <Card key={scenario.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${scenario.color_gradient} flex items-center justify-center`}>
                          <IconComponent className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium">{scenario.name}</h4>
                          <p className="text-xs text-muted-foreground">{scenario.type}</p>
                        </div>
                      </div>
                      {scenario.type === 'custom' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteScenario(scenario.id)}
                          className="hover:bg-red-50 hover:text-red-600"
                        >
                          <XCircle className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{scenario.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}