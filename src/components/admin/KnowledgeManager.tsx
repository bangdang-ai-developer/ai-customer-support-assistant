'use client'

import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Upload, 
  FileText, 
  AlertCircle, 
  Trash2, 
  Eye,
  RefreshCw,
  Search,
  ShoppingCart,
  Monitor,
  Briefcase,
  CheckCircle,
  XCircle,
  FileCheck,
  Sparkles,
  Database,
  Settings,
  ChefHat,
  Heart,
  Scale,
  Building,
  Zap
} from 'lucide-react'

interface KnowledgeEntry {
  id: number
  title: string
  content: string
  category: string
  source: string
  created_at: string
}

interface UploadResult {
  message: string
  chunks_created: number
  total_characters: number
  knowledge_entries: Array<{id: number, title: string}>
}

// Dynamic scenario configuration loaded from API
const defaultScenarioConfig = {
  ECOMMERCE: {
    name: 'E-Commerce Store',
    icon: ShoppingCart,
    color: 'from-green-500 to-emerald-600',
    description: 'Product catalogs, policies, shipping info'
  },
  SAAS: {
    name: 'SaaS Platform', 
    icon: Monitor,
    color: 'from-blue-500 to-cyan-600',
    description: 'Feature docs, API guides, troubleshooting'
  },
  SERVICE_BUSINESS: {
    name: 'Service Business',
    icon: Briefcase,
    color: 'from-purple-500 to-pink-600',
    description: 'Service descriptions, pricing, procedures'
  }
}

interface ScenarioOption {
  id: string
  name: string
  description: string
  icon: string
  color_gradient: string
}

export default function KnowledgeManager() {
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedScenario, setSelectedScenario] = useState('ECOMMERCE')
  const [uploadProgress, setUploadProgress] = useState<string | null>(null)
  const [knowledgeEntries, setKnowledgeEntries] = useState<KnowledgeEntry[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isDragActive, setIsDragActive] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [availableScenarios, setAvailableScenarios] = useState<ScenarioOption[]>([])
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Map icon names to components
  const getIconComponent = (iconName: string) => {
    const iconMap: Record<string, any> = {
      'ShoppingCart': ShoppingCart,
      'Monitor': Monitor,
      'Briefcase': Briefcase,
      'Settings': Settings,
      'ChefHat': ChefHat,
      'Heart': Heart,
      'Scale': Scale,
      'Building': Building,
      'Zap': Zap
    }
    return iconMap[iconName] || Briefcase
  }

  const currentScenario = (() => {
    const scenario = availableScenarios.find(s => s.id === selectedScenario) || {
      id: selectedScenario,
      name: selectedScenario,
      description: 'Custom scenario',
      icon: 'Briefcase',
      color_gradient: 'from-gray-500 to-gray-600'
    }
    
    return {
      ...scenario,
      IconComponent: getIconComponent(scenario.icon)
    }
  })()

  const handleFileUpload = async (file: File) => {
    setIsUploading(true)
    setUploadProgress('🚀 Processing your document...')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('scenario', selectedScenario)
      formData.append('title', file.name.split('.')[0])

      const response = await fetch('http://localhost:8000/api/v1/upload/context', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result: UploadResult = await response.json()
        setUploadProgress(`✨ Success! Created ${result.chunks_created} knowledge entries from ${result.total_characters.toLocaleString()} characters.`)
        await loadKnowledgeEntries()
      } else {
        const error = await response.json()
        setUploadProgress(`❌ Error: ${error.detail}`)
      }
    } catch (error) {
      setUploadProgress(`❌ Upload failed: ${error}`)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const loadKnowledgeEntries = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/upload/context/${selectedScenario}`)
      if (response.ok) {
        const data = await response.json()
        setKnowledgeEntries(data.context_entries)
      }
    } catch (error) {
      console.error('Failed to load knowledge entries:', error)
    }
  }

  const deleteKnowledgeEntry = async (entryId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/upload/context/${entryId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        await loadKnowledgeEntries()
      }
    } catch (error) {
      console.error('Failed to delete entry:', error)
    }
  }

  const testContextSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    setSearchResults([])

    try {
      const formData = new FormData()
      formData.append('query', searchQuery)
      formData.append('scenario', selectedScenario)

      const response = await fetch('http://localhost:8000/api/v1/upload/test-context', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const results = await response.json()
        // Search completed successfully
        setSearchResults(results.results || [])
      } else {
        setSearchResults([])
      }
    } catch (error) {
      console.error('Context search failed:', error)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const loadAvailableScenarios = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/scenarios/')
      if (response.ok) {
        const scenarios = await response.json()
        
        // Convert API response to component format
        const formattedScenarios = scenarios.map((scenario: any) => ({
          id: scenario.id,
          name: scenario.name,
          description: scenario.description,
          icon: scenario.icon || 'Briefcase',
          color_gradient: scenario.color_gradient || 'from-gray-500 to-gray-600'
        }))
        
        setAvailableScenarios(formattedScenarios)
        
        // If current selection is not in available scenarios, select first one
        if (!formattedScenarios.find((s: any) => s.id === selectedScenario)) {
          setSelectedScenario(formattedScenarios[0]?.id || 'ECOMMERCE')
        }
      }
    } catch (error) {
      console.error('Failed to load scenarios:', error)
      // Fallback to default scenarios
      const fallbackScenarios = Object.entries(defaultScenarioConfig).map(([id, config]) => ({
        id,
        name: config.name,
        description: config.description,
        icon: config.icon.name,
        color_gradient: config.color
      }))
      setAvailableScenarios(fallbackScenarios)
    }
  }

  React.useEffect(() => {
    loadAvailableScenarios()
  }, [])

  React.useEffect(() => {
    loadKnowledgeEntries()
  }, [selectedScenario])

  return (
    <div className="space-y-6">
      {/* Enhanced Scenario Selection */}
      <Card className="border-0 shadow-lg">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${currentScenario.color_gradient} flex items-center justify-center shadow-md`}>
              <currentScenario.IconComponent className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl">Business Scenario Configuration</CardTitle>
              <CardDescription>
                Select the business type to customize AI responses and upload relevant context documents.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {availableScenarios.map((scenario) => {
              const IconComponent = getIconComponent(scenario.icon || 'Briefcase')

              return (
                <Card 
                  key={scenario.id} 
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    selectedScenario === scenario.id 
                      ? 'ring-2 ring-blue-500 shadow-lg' 
                      : 'hover:bg-accent/50'
                  }`}
                  onClick={() => setSelectedScenario(scenario.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${scenario.color_gradient} flex items-center justify-center`}>
                        <IconComponent className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-sm">{scenario.name}</div>
                        <div className="text-xs text-muted-foreground">{scenario.description}</div>
                      </div>
                      {selectedScenario === scenario.id && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 bg-muted/50">
          <TabsTrigger value="upload" className="flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Upload Context
          </TabsTrigger>
          <TabsTrigger value="manage" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Manage Context
          </TabsTrigger>
          <TabsTrigger value="test" className="flex items-center gap-2">
            <Search className="w-4 h-4" />
            Test Search
          </TabsTrigger>
        </TabsList>

        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-4">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Upload className="w-5 h-5 text-white" />
                </div>
                <div>
                  <CardTitle>Upload Business Context</CardTitle>
                  <CardDescription>
                    Upload documents to enhance your {currentScenario.name.toLowerCase()} AI responses with business-specific knowledge.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onDragEnter={() => setIsDragActive(true)}
                onDragLeave={() => setIsDragActive(false)}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
                  isDragActive 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/50 scale-105' 
                    : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50/50 dark:hover:bg-gray-800/50'
                } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
              >
                <div className="space-y-4">
                  <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center transition-colors ${
                    isDragActive ? 'bg-blue-500' : 'bg-gray-100 dark:bg-gray-800'
                  }`}>
                    <Upload className={`w-8 h-8 ${isDragActive ? 'text-white' : 'text-gray-400'}`} />
                  </div>
                  
                  {isDragActive ? (
                    <div>
                      <p className="text-lg font-medium text-blue-600">Drop your file here!</p>
                      <p className="text-sm text-blue-500">We'll process it automatically</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-lg font-medium mb-2">
                        Drag & drop your business document
                      </p>
                      <p className="text-sm text-muted-foreground mb-4">
                        Supports <span className="font-medium">PDF</span>, <span className="font-medium">Word</span>, <span className="font-medium">Markdown</span>, and <span className="font-medium">Text</span> files
                      </p>
                      <div className="space-y-2">
                        <input
                          type="file"
                          accept=".pdf,.docx,.txt,.md"
                          onChange={handleFileSelect}
                          className="hidden"
                          id="file-upload"
                          disabled={isUploading}
                        />
                        <Label htmlFor="file-upload" className="cursor-pointer">
                          <Button asChild disabled={isUploading}>
                            <span className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                              {isUploading ? (
                                <>
                                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                  Processing...
                                </>
                              ) : (
                                <>
                                  <FileCheck className="w-4 h-4 mr-2" />
                                  Choose File
                                </>
                              )}
                            </span>
                          </Button>
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Maximum file size: 10MB
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {uploadProgress && (
                <Alert className={`mt-6 border-0 shadow-md ${
                  uploadProgress.includes('Success') || uploadProgress.includes('✨')
                    ? 'bg-green-50 dark:bg-green-950 text-green-800 dark:text-green-200'
                    : 'bg-red-50 dark:bg-red-950 text-red-800 dark:text-red-200'
                }`}>
                  <div className="flex items-center gap-2">
                    {uploadProgress.includes('Success') || uploadProgress.includes('✨') ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                    <AlertDescription className="font-medium">
                      {uploadProgress}
                    </AlertDescription>
                  </div>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Manage Tab */}
        <TabsContent value="manage" className="space-y-4">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                    <Database className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle>Context Library</CardTitle>
                    <CardDescription>
                      Manage uploaded documents for {currentScenario.name.toLowerCase()}.
                    </CardDescription>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={loadKnowledgeEntries}
                  size="sm"
                  className="hover:bg-accent"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {knowledgeEntries.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 mx-auto rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4">
                      <FileText className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="font-medium mb-2">No context documents yet</h3>
                    <p className="text-muted-foreground mb-4">
                      Upload business documents to make your AI assistant smarter.
                    </p>
                    <Button 
                      onClick={() => setActiveTab('upload')}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Your First Document
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {knowledgeEntries.map((entry) => (
                      <Card key={entry.id} className="hover:shadow-md transition-shadow border-l-4 border-l-blue-500">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <FileCheck className="w-4 h-4 text-green-500" />
                                <h4 className="font-medium">{entry.title}</h4>
                              </div>
                              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                                {entry.content}
                              </p>
                              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <FileText className="w-3 h-3" />
                                  {entry.source}
                                </span>
                                <span>
                                  {new Date(entry.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                            <div className="flex space-x-2 ml-4">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {/* View entry functionality */}}
                                className="hover:bg-blue-50 hover:border-blue-200"
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => deleteKnowledgeEntry(entry.id)}
                                className="hover:bg-red-50 hover:border-red-200 hover:text-red-600"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Test Tab */}
        <TabsContent value="test" className="space-y-4">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <Search className="w-5 h-5 text-white" />
                </div>
                <div>
                  <CardTitle>Context Search Testing</CardTitle>
                  <CardDescription>
                    Test how well your uploaded context documents help answer specific customer questions.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="search-query" className="text-sm font-medium">
                  Customer Question
                </Label>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search-query"
                    placeholder="e.g., 'What's your return policy?' or 'How do I cancel my subscription?'"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Button 
                onClick={testContextSearch} 
                className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
                disabled={!searchQuery.trim() || isSearching}
              >
                {isSearching ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Test AI Context Search
                  </>
                )}
              </Button>

              {/* Search Results Display */}
              {searchResults.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <h4 className="font-medium">Search Results ({searchResults.length} found)</h4>
                  </div>
                  
                  <div className="space-y-3">
                    {searchResults.map((result, index) => (
                      <Card key={index} className="border-l-4 border-l-green-500">
                        <CardContent className="p-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <FileCheck className="w-4 h-4 text-green-500" />
                              <h5 className="font-medium">{result.title}</h5>
                            </div>
                            <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded">
                              {result.content}
                            </p>
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <FileText className="w-3 h-3" />
                                Source: {result.source}
                              </span>
                              {result.similarity_score && (
                                <span className="flex items-center gap-1">
                                  <Sparkles className="w-3 h-3" />
                                  Relevance: {(result.similarity_score * 100).toFixed(1)}%
                                </span>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* No Results Message */}
              {!isSearching && searchQuery && searchResults.length === 0 && (
                <Alert className="border-0 bg-amber-50 dark:bg-amber-950">
                  <AlertCircle className="h-4 w-4 text-amber-600" />
                  <AlertDescription className="text-amber-800 dark:text-amber-200">
                    No relevant context found for "{searchQuery}". Try uploading more specific business documents for this scenario.
                  </AlertDescription>
                </Alert>
              )}

              <div className="bg-muted/50 rounded-lg p-4">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-blue-500" />
                  How it works
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Your question is analyzed using AI embeddings</li>
                  <li>• Relevant sections from uploaded documents are found</li>
                  <li>• Context is injected into AI responses for accuracy</li>
                  <li>• Results show which documents influenced the answer</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}