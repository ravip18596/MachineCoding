package main

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

type CacheEntry struct {
	value      interface{}
	expiration time.Time
}

// Cache In-memory cache
type Cache struct {
	data  map[string]CacheEntry
	mutex sync.RWMutex
	ttl   time.Duration
}

func NewCache(ttl time.Duration) *Cache {
	return &Cache{
		data:  make(map[string]CacheEntry),
		ttl:   ttl,
		mutex: sync.RWMutex{},
	}
}

func (c *Cache) Set(key string, value interface{}) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	c.data[key] = CacheEntry{
		value:      value,
		expiration: time.Now().Add(c.ttl),
	}
}

func (c *Cache) Get(key string) interface{} {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	entry, ok := c.data[key]
	if !ok {
		return nil
	}
	if time.Now().After(entry.expiration) {
		c.mutex.Lock()
		defer c.mutex.Unlock()
		delete(c.data, key)
		return nil
	}
	return entry.value
}

func (c *Cache) Delete(key string) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	delete(c.data, key)
}

func TestCache(t *testing.T) {
	cache := NewCache(1 * time.Second)
	cache.Set("foo", "bar")
	value := cache.Get("foo")
	if value != "bar" {
		t.Errorf("value should be bar")
	}

	time.Sleep(2 * time.Second)
	value = cache.Get("foo")
	if value != nil {
		t.Errorf("value should be nil, got %v", value)
	}

	// Test Delete
	cache.Set("foo2", "bar2")
	cache.Delete("foo2")
	value = cache.Get("foo2")
	if value != nil {
		t.Errorf("value should be nil after delete, got %v", value)
	}

	// Test concurrent access
	cache = NewCache(5 * time.Second)
	numGoRoutines := 100
	key := "concurrentKey"
	expectedValue := "concurrentValue"
	cache.Set(key, expectedValue)

	var wg sync.WaitGroup
	wg.Add(numGoRoutines)

	for i := 0; i < numGoRoutines; i++ {
		go func() {
			defer wg.Done()
			val := cache.Get(key)
			if val != expectedValue {
				t.Errorf("Concurrent Get failed: expected %v, got %v", expectedValue, val)
			}
		}()
	}
	wg.Wait()
}

func main() {
	cache := NewCache(5 * time.Second)
	cache.Set("myKey", "Hello, Cache!")
	val := cache.Get("myKey")
	fmt.Println(val)
	time.Sleep(6 * time.Second)
	val = cache.Get("myKey")
	fmt.Println(val)
}
